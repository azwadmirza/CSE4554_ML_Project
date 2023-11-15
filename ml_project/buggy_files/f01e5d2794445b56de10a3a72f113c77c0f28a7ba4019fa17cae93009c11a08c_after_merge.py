    def __default_containers_resolvers(self):
        default_resolvers = [
            ExplicitContainerResolver(self.app_info),
            ExplicitSingularityContainerResolver(self.app_info),
        ]
        if self.enable_mulled_containers:
            default_resolvers.extend([
                CachedMulledDockerContainerResolver(self.app_info, namespace="biocontainers"),
                CachedMulledDockerContainerResolver(self.app_info, namespace="local"),
                CachedMulledSingularityContainerResolver(self.app_info, namespace="biocontainers"),
                CachedMulledSingularityContainerResolver(self.app_info, namespace="local"),
                MulledDockerContainerResolver(self.app_info, namespace="biocontainers"),
                MulledSingularityContainerResolver(self.app_info, namespace="biocontainers"),
            ])
            # BuildMulledDockerContainerResolver and BuildMulledSingularityContainerResolver both need the docker daemon to build images.
            # If docker is not available, we don't load them.
            build_mulled_docker_container_resolver = BuildMulledDockerContainerResolver(self.app_info)
            if build_mulled_docker_container_resolver.docker_cli_available:
                default_resolvers.extend([
                    build_mulled_docker_container_resolver,
                    BuildMulledSingularityContainerResolver(self.app_info),
                ])
        return default_resolvers