    def check(self, instance):
        config = self.get_config(instance)
        if config is None:
            return

        tags = list(config['tags'])

        # We access the version of the Vault API corresponding to each instance's `api_url`.
        try:
            config['api']['check_leader'](config, tags)
            config['api']['check_health'](config, tags)
        except ApiUnreachable:
            return

        self.service_check(self.SERVICE_CHECK_CONNECT, AgentCheck.OK, tags=tags)