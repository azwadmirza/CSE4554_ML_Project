    def cached_container_description(self, targets, namespace, hash_func, resolution_cache):
        return docker_cached_container_description(targets, namespace, hash_func, resolution_cache)