    def check(self, instance):
        config = self.get_config(instance)
        if config is None:
            return

        api = config['api']
        tags = list(config['tags'])

        # We access the version of the Vault API corresponding to each instance's `api_url`.
        try:
            api['check_leader'](config, tags)
            api['check_health'](config, tags)
        except ApiUnreachable:
            return

        self.service_check(self.SERVICE_CHECK_CONNECT, AgentCheck.OK, tags=tags)