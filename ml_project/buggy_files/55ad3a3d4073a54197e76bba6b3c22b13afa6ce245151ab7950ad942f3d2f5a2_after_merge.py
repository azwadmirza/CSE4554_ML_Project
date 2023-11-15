    def cached_container_description(self, targets, namespace, hash_func, resolution_cache):
        try:
            return docker_cached_container_description(targets, namespace, hash_func, resolution_cache)
        except subprocess.CalledProcessError:
            # We should only get here if a docker binary is available, but command quits with a non-zero exit code,
            # e.g if the docker daemon is not available
            log.exception('An error occured while listing cached docker image. Docker daemon may need to be restarted.')
            return None