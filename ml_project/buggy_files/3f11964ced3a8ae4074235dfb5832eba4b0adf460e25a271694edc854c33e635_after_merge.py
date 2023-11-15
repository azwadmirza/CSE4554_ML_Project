    def create(transport, path, config):
        personality = transport.worker.personality
        personality.WEB_SERVICE_CHECKERS['webhook'](personality, config)

        # create a vanilla session: the webhook will use this to inject events
        #
        webhook_session_config = ComponentConfig(realm=config['realm'], extra=None)
        webhook_session = ApplicationSession(webhook_session_config)

        # add the webhook session to the router
        #
        router = transport._worker._router_session_factory._routerFactory._routers[config['realm']]
        transport._worker._router_session_factory.add(webhook_session,
                                                      router,
                                                      authrole=config.get('role', 'anonymous'))

        # now create the webhook Twisted Web resource
        #
        resource = WebhookResource(config.get('options', {}), webhook_session)

        return RouterWebServiceWebhook(transport, path, config, resource)