    def detect_use_config_proxy(client):
        return client.params['build'] and client.params['build']['use_config_proxy'] is not None