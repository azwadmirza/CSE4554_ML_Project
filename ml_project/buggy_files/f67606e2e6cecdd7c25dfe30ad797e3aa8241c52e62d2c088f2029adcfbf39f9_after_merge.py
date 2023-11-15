    def register_resource(klass, registry, event):
        for rtype, resource_manager in registry.items():
            if not resource_manager.has_arn():
                continue
            if 'post-finding' in resource_manager.action_registry:
                continue
            resource_manager.action_registry.register('post-finding', klass)