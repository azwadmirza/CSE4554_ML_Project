    def start_router_transport(self, id, config, details=None):
        """
        Start a transport on this router worker.

        :param id: The ID of the transport to start.
        :type id: str
        :param config: The transport configuration.
        :type config: dict
        """
        self.log.debug("{name}.start_router_transport", name=self.__class__.__name__)

        # prohibit starting a transport twice
        #
        if id in self.transports:
            emsg = "Could not start transport: a transport with ID '{}' is already running (or starting)".format(id)
            self.log.error(emsg)
            raise ApplicationError(u'crossbar.error.already_running', emsg)

        # check configuration
        #
        try:
            checkconfig.check_router_transport(config)
        except Exception as e:
            emsg = "Invalid router transport configuration: {}".format(e)
            self.log.error(emsg)
            raise ApplicationError(u"crossbar.error.invalid_configuration", emsg)
        else:
            self.log.debug("Starting {ttype}-transport on router.", ttype=config['type'])

        # standalone WAMP-RawSocket transport
        #
        if config['type'] == 'rawsocket':

            transport_factory = WampRawSocketServerFactory(self._router_session_factory, config)
            transport_factory.noisy = False

        # standalone WAMP-WebSocket transport
        #
        elif config['type'] == 'websocket':

            transport_factory = WampWebSocketServerFactory(self._router_session_factory, self.config.extra.cbdir, config, self._templates)
            transport_factory.noisy = False

        # Flash-policy file server pseudo transport
        #
        elif config['type'] == 'flashpolicy':

            transport_factory = FlashPolicyFactory(config.get('allowed_domain', None), config.get('allowed_ports', None))

        # WebSocket testee pseudo transport
        #
        elif config['type'] == 'websocket.testee':

            transport_factory = WebSocketTesteeServerFactory(config, self._templates)

        # Stream testee pseudo transport
        #
        elif config['type'] == 'stream.testee':

            transport_factory = StreamTesteeServerFactory()

        # MQTT legacy adapter transport
        #
        elif config['type'] == 'mqtt':

            transport_factory = WampMQTTServerFactory(
                self._router_session_factory, config, self._reactor)
            transport_factory.noisy = False

        # Twisted Web based transport
        #
        elif config['type'] == 'web':

            transport_factory = self._create_web_factory(
                config,
                is_secure=u'tls' in config[u'endpoint'],
            )

        # Universal transport
        #
        elif config['type'] == 'universal':
            if 'web' in config:
                web_factory = self._create_web_factory(
                    config['web'],
                    is_secure=(u'tls' in config['endpoint']),
                )
            else:
                web_factory = None

            if 'rawsocket' in config:
                rawsocket_factory = WampRawSocketServerFactory(self._router_session_factory, config['rawsocket'])
                rawsocket_factory.noisy = False
            else:
                rawsocket_factory = None

            if 'mqtt' in config:
                mqtt_factory = WampMQTTServerFactory(
                    self._router_session_factory, config['mqtt'], self._reactor)
                mqtt_factory.noisy = False
            else:
                mqtt_factory = None

            if 'websocket' in config:
                websocket_factory_map = {}
                for websocket_url_first_component, websocket_config in config['websocket'].items():
                    websocket_transport_factory = WampWebSocketServerFactory(self._router_session_factory, self.config.extra.cbdir, websocket_config, self._templates)
                    websocket_transport_factory.noisy = False
                    websocket_factory_map[websocket_url_first_component] = websocket_transport_factory
                    self.log.debug('hooked up websocket factory on request URI {request_uri}', request_uri=websocket_url_first_component)
            else:
                websocket_factory_map = None

            transport_factory = UniSocketServerFactory(web_factory, websocket_factory_map, rawsocket_factory, mqtt_factory)

        # Unknown transport type
        #
        else:
            # should not arrive here, since we did check_transport() in the beginning
            raise Exception("logic error")

        # create transport endpoint / listening port from transport factory
        #
        d = create_listening_port_from_config(config['endpoint'],
                                              self.config.extra.cbdir,
                                              transport_factory,
                                              self._reactor,
                                              self.log)

        def ok(port):
            self.transports[id] = RouterTransport(id, config, transport_factory, port)
            self.log.debug("Router transport '{id}'' started and listening", id=id)
            return

        def fail(err):
            emsg = "Cannot listen on transport endpoint: {log_failure}"
            self.log.error(emsg, log_failure=err)
            raise ApplicationError(u"crossbar.error.cannot_listen", emsg)

        d.addCallbacks(ok, fail)
        return d