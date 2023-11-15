    def detect_use_config_proxy(client):
        return client.module.params['build'] and client.module.params['build'].get('use_config_proxy') is not None