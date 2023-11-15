    def create(transport, path, config):
        personality = transport.worker.personality
        personality.WEB_SERVICE_CHECKERS['publisher'](personality, config)

        # create a vanilla session: the publisher will use this to inject events
        #
        publisher_session_config = ComponentConfig(realm=config['realm'], extra=None)
        publisher_session = ApplicationSession(publisher_session_config)

        # add the publisher session to the router
        #
        router = transport._worker._router_session_factory._routerFactory._routers[config['realm']]
        transport._worker._router_session_factory.add(publisher_session,
                                                      router,
                                                      authrole=config.get('role', 'anonymous'))

        # now create the publisher Twisted Web resource
        #
        resource = PublisherResource(config.get('options', {}), publisher_session)

        return RouterWebServiceRestPublisher(transport, path, config, resource)