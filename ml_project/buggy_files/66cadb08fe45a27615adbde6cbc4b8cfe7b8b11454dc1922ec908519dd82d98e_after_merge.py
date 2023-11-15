    def resolve(self, enabled_container_types, tool_info, **kwds):
        if not self.docker_cli_available or tool_info.requires_galaxy_python_environment or self.container_type not in enabled_container_types:
            return None

        targets = mulled_targets(tool_info)
        resolution_cache = kwds.get("resolution_cache")
        return docker_cached_container_description(targets, self.namespace, hash_func=self.hash_func, shell=self.shell, resolution_cache=resolution_cache)