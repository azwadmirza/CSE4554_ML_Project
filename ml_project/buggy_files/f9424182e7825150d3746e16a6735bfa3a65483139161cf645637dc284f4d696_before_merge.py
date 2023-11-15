    def get_service_scale(self, service_dict):
        # service.scale for v2 and deploy.replicas for v3
        scale = service_dict.get('scale', None)
        deploy_dict = service_dict.get('deploy', None)
        if not deploy_dict:
            return 1 if scale is None else scale

        if deploy_dict.get('mode', 'replicated') != 'replicated':
            return 1 if scale is None else scale

        replicas = deploy_dict.get('replicas', None)
        if scale and replicas:
            raise ConfigurationError(
                "Both service.scale and service.deploy.replicas are set."
                " Only one of them must be set."
            )
        if replicas:
            scale = replicas
        # deploy may contain placement constraints introduced in v3.8
        max_replicas = deploy_dict.get('placement', {}).get(
            'max_replicas_per_node',
            scale)

        scale = min(scale, max_replicas)
        if max_replicas < scale:
            log.warning("Scale is limited to {} ('max_replicas_per_node' field).".format(
                max_replicas))
        return scale