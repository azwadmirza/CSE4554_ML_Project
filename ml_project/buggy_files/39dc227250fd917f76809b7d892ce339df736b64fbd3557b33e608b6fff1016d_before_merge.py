    def detect_build_cache_from(client):
        return client.params['build'] and client.params['build']['cache_from'] is not None