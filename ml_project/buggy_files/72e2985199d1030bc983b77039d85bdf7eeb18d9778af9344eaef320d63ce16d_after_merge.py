    def _parse_and_create_resource(logical_id, resource_json, resources_map, region_name, update=False):
        stack_name = resources_map.get('AWS::StackName')
        resource_hash_key = (stack_name, logical_id)

        # If the current stack is being updated, avoid infinite recursion
        updating = CURRENTLY_UPDATING_RESOURCES.get(resource_hash_key)
        LOG.debug('Currently updating stack resource %s/%s: %s' % (stack_name, logical_id, updating))
        if updating:
            return None

        # parse and get final resource JSON
        resource_tuple = parsing.parse_resource(logical_id, resource_json, resources_map)
        if not resource_tuple:
            return None
        _, resource_json, _ = resource_tuple

        # add some missing default props which otherwise cause deployments to fail
        props = resource_json['Properties'] = resource_json.get('Properties') or {}
        if resource_json['Type'] == 'AWS::Lambda::EventSourceMapping' and not props.get('StartingPosition'):
            props['StartingPosition'] = 'LATEST'

        # check if this resource already exists in the resource map
        resource = resources_map._parsed_resources.get(logical_id)
        if resource and not update:
            return resource

        # check whether this resource needs to be deployed
        resource_wrapped = {logical_id: resource_json}
        should_be_created = template_deployer.should_be_deployed(logical_id, resource_wrapped, stack_name)
        if not should_be_created:
            # This resource is either not deployable or already exists. Check if it can be updated
            if not template_deployer.is_updateable(logical_id, resource_wrapped, stack_name):
                LOG.debug('Resource %s need not be deployed: %s' % (logical_id, resource_json))
                if resource:
                    return resource

        # fix resource ARNs, make sure to convert account IDs 000000000000 to 123456789012
        resource_json_arns_fixed = clone(json_safe(convert_objs_to_ids(resource_json)))
        set_moto_account_ids(resource_json_arns_fixed)
        # create resource definition and store CloudFormation metadata in moto
        if resource or update:
            parse_and_update_resource_orig(logical_id,
                resource_json_arns_fixed, resources_map, region_name)
        elif not resource:
            resource = parse_and_create_resource_orig(logical_id,
                resource_json_arns_fixed, resources_map, region_name)
        # Fix for moto which sometimes hard-codes region name as 'us-east-1'
        if hasattr(resource, 'region_name') and resource.region_name != region_name:
            LOG.debug('Updating incorrect region from %s to %s' % (resource.region_name, region_name))
            resource.region_name = region_name

        # Apply some fixes/patches to the resource names, then deploy resource in LocalStack
        update_resource_name(resource, resource_json)
        LOG.debug('Deploying CloudFormation resource: %s' % resource_json)

        try:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = True
            deploy_func = template_deployer.update_resource if update else template_deployer.deploy_resource
            result = deploy_func(logical_id, resource_wrapped, stack_name=stack_name)
        finally:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = False

        if not should_be_created:
            # skip the parts below for update requests
            return resource

        def find_id(resource):
            """ Find ID of the given resource. """
            for id_attr in ('Id', 'id', 'ResourceId', 'RestApiId', 'DeploymentId'):
                if id_attr in resource:
                    return resource[id_attr]

        # update resource IDs to avoid mismatch between CF moto and LocalStack backend resources
        if hasattr(resource, 'id') or (isinstance(resource, dict) and resource.get('id')):
            existing_id = resource.id if hasattr(resource, 'id') else resource['id']
            new_res_id = find_id(result)
            LOG.debug('Updating resource id: %s - %s, %s - %s' % (existing_id, new_res_id, resource, resource_json))
            if new_res_id:
                LOG.info('Updating resource ID from %s to %s (%s)' % (existing_id, new_res_id, region_name))
                update_resource_id(resource, new_res_id, props, region_name)
            else:
                LOG.warning('Unable to extract id for resource %s: %s' % (logical_id, result))

        # update physical_resource_id field
        update_physical_resource_id(resource)

        return resource