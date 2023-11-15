    def start(self):
        """
        Starts this node. This will start a node controller and then spawn new worker
        processes as needed.
        """
        if not self._config:
            raise Exception("No node configuration set")

        # get controller config/options
        #
        controller_config = self._config.get('controller', {})
        controller_options = controller_config.get('options', {})

        # set controller process title
        #
        try:
            import setproctitle
        except ImportError:
            self.log.warn("Warning, could not set process title (setproctitle not installed)")
        else:
            setproctitle.setproctitle(controller_options.get('title', 'crossbar-controller'))

        # local node management router
        #
        self._router_factory = RouterFactory(None)
        self._router_session_factory = RouterSessionFactory(self._router_factory)
        rlm_config = {
            'name': self._realm
        }
        rlm = RouterRealm(None, rlm_config)
        router = self._router_factory.start_realm(rlm)

        # setup global static roles
        #
        self._add_global_roles()

        # always add a realm service session
        #
        cfg = ComponentConfig(self._realm)
        rlm.session = (self.ROUTER_SERVICE)(cfg, router)
        self._router_session_factory.add(rlm.session, authrole=u'trusted')
        self.log.debug('Router service session attached [{router_service}]', router_service=qual(self.ROUTER_SERVICE))

        # add the node controller singleton component
        #
        self._controller = self.NODE_CONTROLLER(self)

        self._router_session_factory.add(self._controller, authrole=u'trusted')
        self.log.debug('Node controller attached [{node_controller}]', node_controller=qual(self.NODE_CONTROLLER))

        # add extra node controller components
        #
        self._add_extra_controller_components(controller_options)

        # setup Node shutdown triggers
        #
        self._set_shutdown_triggers(controller_options)

        panic = False
        try:
            # startup the node personality ..
            yield self._startup()

            # .. and notify systemd that we are fully up and running
            try:
                import sdnotify
                sdnotify.SystemdNotifier().notify("READY=1")
            except:
                # do nothing on non-systemd platforms
                pass

        except ApplicationError as e:
            panic = True
            self.log.error("{msg}", msg=e.error_message())

        except Exception:
            panic = True
            self.log.failure('Could not startup node: {log_failure.value}')

        if panic:
            try:
                self._reactor.stop()
            except twisted.internet.error.ReactorNotRunning:
                pass