    def detect_build_cache_from(client):
        return client.module.params['build'] and client.module.params['build'].get('cache_from') is not None