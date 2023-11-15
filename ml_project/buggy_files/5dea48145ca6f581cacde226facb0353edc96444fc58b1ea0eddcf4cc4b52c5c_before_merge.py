    def create(transport, path, config):
        personality = transport.worker.personality
        personality.WEB_SERVICE_CHECKERS['caller'](personality, config)

        # create a vanilla session: the caller will use this to inject calls
        #
        caller_session_config = ComponentConfig(realm=config['realm'], extra=None)
        caller_session = ApplicationSession(caller_session_config)

        # add the calling session to the router
        #
        transport._worker._router_session_factory.add(caller_session,
                                                      authrole=config.get('role', 'anonymous'))

        # now create the caller Twisted Web resource
        #
        resource = CallerResource(
            config.get('options', {}),
            caller_session
        )

        return RouterWebServiceRestCaller(transport, path, config, resource)