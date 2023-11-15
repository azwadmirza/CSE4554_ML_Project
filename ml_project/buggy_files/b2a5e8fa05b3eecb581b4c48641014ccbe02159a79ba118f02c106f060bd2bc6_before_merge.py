    def resolve(self, enabled_container_types, tool_info, install=False, **kwds):
        if tool_info.requires_galaxy_python_environment or self.container_type not in enabled_container_types:
            return None

        targets = mulled_targets(tool_info)
        if len(targets) == 0:
            return None
        if self.auto_install or install:
            mull_targets(
                targets,
                involucro_context=self._get_involucro_context(),
                **self._mulled_kwds
            )
        return docker_cached_container_description(targets, self.namespace, hash_func=self.hash_func, shell=self.shell)