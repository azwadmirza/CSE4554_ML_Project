    def detect_build_network(client):
        return client.module.params['build'] and client.module.params['build'].get('network') is not None