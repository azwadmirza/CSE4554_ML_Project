    def detect_build_network(client):
        return client.params['build'] and client.params['build']['network'] is not None