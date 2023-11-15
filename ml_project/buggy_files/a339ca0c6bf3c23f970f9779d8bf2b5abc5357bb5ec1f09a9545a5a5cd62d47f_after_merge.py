        def run_loop(*args):
            # NOTE: We're adding this additional loop, as it seems that in some cases moto
            #   does not consider resource dependencies (e.g., if a "DependsOn" resource property
            #   is defined). This loop allows us to incrementally resolve such dependencies.
            resource_map = self.resource_map
            unresolved = {}
            for i in range(MAX_DEPENDENCY_DEPTH):
                unresolved = getattr(resource_map, '_unresolved_resources', {})
                if not unresolved:
                    set_status('CREATE_COMPLETE')
                    return resource_map
                resource_map._unresolved_resources = {}
                for resource_id, resource_details in unresolved.items():
                    # Re-trigger the resource creation
                    parse_and_create_resource(*resource_details, force_create=True)
                if unresolved.keys() == resource_map._unresolved_resources.keys():
                    # looks like no more resources can be resolved -> bail
                    LOG.warning('Unresolvable dependencies, there may be undeployed stack resources: %s' % unresolved)
                    break
            set_status('CREATE_FAILED')
            raise Exception('Unable to resolve all CloudFormation resources after traversing ' +
                'dependency tree (maximum depth %s reached): %s' % (MAX_DEPENDENCY_DEPTH, unresolved.keys()))