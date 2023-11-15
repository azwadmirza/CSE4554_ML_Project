    def resolve(self, enabled_container_types, tool_info, install=False, session=None, **kwds):
        resolution_cache = kwds.get("resolution_cache")
        if tool_info.requires_galaxy_python_environment or self.container_type not in enabled_container_types:
            return None

        targets = mulled_targets(tool_info)
        if len(targets) == 0:
            return None

        name = targets_to_mulled_name(targets=targets, hash_func=self.hash_func, namespace=self.namespace, resolution_cache=resolution_cache, session=session)
        if name:
            container_id = "quay.io/{}/{}".format(self.namespace, name)
            if self.protocol:
                container_id = "{}{}".format(self.protocol, container_id)
            container_description = ContainerDescription(
                container_id,
                type=self.container_type,
                shell=self.shell,
            )
            if self.docker_cli_available:
                if install and not self.cached_container_description(
                        targets,
                        namespace=self.namespace,
                        hash_func=self.hash_func,
                        resolution_cache=resolution_cache,
                ):
                    destination_info = {}
                    destination_for_container_type = kwds.get('destination_for_container_type')
                    if destination_for_container_type:
                        destination_info = destination_for_container_type(self.container_type)
                    container = CONTAINER_CLASSES[self.container_type](container_description.identifier,
                                                                       self.app_info,
                                                                       tool_info,
                                                                       destination_info,
                                                                       {},
                                                                       container_description)
                    self.pull(container)
                if not self.auto_install:
                    container_description = self.cached_container_description(
                        targets,
                        namespace=self.namespace,
                        hash_func=self.hash_func,
                        resolution_cache=resolution_cache,
                    )
            return container_description