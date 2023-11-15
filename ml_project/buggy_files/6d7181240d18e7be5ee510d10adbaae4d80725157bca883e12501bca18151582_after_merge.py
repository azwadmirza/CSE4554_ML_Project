    def _parse_and_create_resource(logical_id, resource_json, resources_map, region_name,
            update=False, force_create=False):
        stack_name = resources_map.get('AWS::StackName')
        resource_hash_key = (stack_name, logical_id)
        props = resource_json['Properties'] = resource_json.get('Properties') or {}

        # If the current stack is being updated, avoid infinite recursion
        updating = CURRENTLY_UPDATING_RESOURCES.get(resource_hash_key)
        LOG.debug('Currently processing stack resource %s/%s: %s' % (stack_name, logical_id, updating))
        if updating:
            return None

        # parse and get final resource JSON
        resource_tuple = parsing.parse_resource(logical_id, resource_json, resources_map)
        if not resource_tuple:
            return None
        _, resource_json, _ = resource_tuple

        def add_default_props(resource_props):
            """ apply some fixes which otherwise cause deployments to fail """
            res_type = resource_props['Type']
            props = resource_props.get('Properties', {})
            if res_type == 'AWS::Lambda::EventSourceMapping' and not props.get('StartingPosition'):
                props['StartingPosition'] = 'LATEST'
            # generate default names for certain resource types
            default_attrs = (('AWS::IAM::Role', 'RoleName'), ('AWS::Events::Rule', 'Name'))
            for entry in default_attrs:
                if res_type == entry[0] and not props.get(entry[1]):
                    props[entry[1]] = 'cf-%s-%s' % (stack_name, md5(canonical_json(props)))

        # add some fixes and default props which otherwise cause deployments to fail
        add_default_props(resource_json)
        for resource in resources_map._resource_json_map.values():
            add_default_props(resource)

        # check if this resource already exists in the resource map
        resource = resources_map._parsed_resources.get(logical_id)
        if resource and not update and not force_create:
            return resource

        # fix resource ARNs, make sure to convert account IDs 000000000000 to 123456789012
        resource_json_arns_fixed = clone(json_safe(convert_objs_to_ids(resource_json)))
        set_moto_account_ids(resource_json_arns_fixed)

        # create resource definition and store CloudFormation metadata in moto
        moto_create_error = None
        if (resource or update) and not force_create:
            parse_and_update_resource_orig(logical_id, resource_json_arns_fixed, resources_map, region_name)
        elif not resource:
            try:
                resource = parse_and_create_resource_orig(
                    logical_id, resource_json_arns_fixed, resources_map, region_name
                )
                if not resource:
                    # this can happen if the resource has an associated Condition which evaluates to false
                    return resource
                resource.logical_id = logical_id
            except Exception as e:
                moto_create_error = e

        # check whether this resource needs to be deployed
        resource_map_new = dict(resources_map._resource_json_map)
        resource_map_new[logical_id] = resource_json
        should_be_created = template_deployer.should_be_deployed(logical_id, resource_map_new, stack_name)

        # check for moto creation errors and raise an exception if needed
        if moto_create_error:
            if should_be_created:
                raise moto_create_error
            else:
                LOG.info('Error on moto CF resource creation. Ignoring, as should_be_created=%s: %s' %
                         (should_be_created, moto_create_error))

        # Fix for moto which sometimes hard-codes region name as 'us-east-1'
        if hasattr(resource, 'region_name') and resource.region_name != region_name:
            LOG.debug('Updating incorrect region from %s to %s' % (resource.region_name, region_name))
            resource.region_name = region_name

        # check whether this resource needs to be deployed
        is_updateable = False
        if not should_be_created:
            # This resource is either not deployable or already exists. Check if it can be updated
            is_updateable = template_deployer.is_updateable(logical_id, resource_map_new, stack_name)
            if not update or not is_updateable:
                all_satisfied = template_deployer.all_resource_dependencies_satisfied(
                    logical_id, resource_map_new, stack_name
                )
                if not all_satisfied:
                    LOG.info('Resource %s cannot be deployed, found unsatisfied dependencies. %s' % (
                        logical_id, resource_json))
                    details = [logical_id, resource_json, resources_map, region_name]
                    resources_map._unresolved_resources = getattr(resources_map, '_unresolved_resources', {})
                    resources_map._unresolved_resources[logical_id] = details
                else:
                    LOG.debug('Resource %s need not be deployed (is_updateable=%s): %s %s' % (
                        logical_id, is_updateable, resource_json, bool(resource)))
                # Return if this resource already exists and can/need not be updated yet
                # NOTE: We should always return the resource here, to avoid duplicate
                #       creation of resources in moto!
                return resource

        # Apply some fixes/patches to the resource names, then deploy resource in LocalStack
        update_resource_name(resource, resource_json)
        LOG.debug('Deploying CloudFormation resource (update=%s, exists=%s, updateable=%s): %s' %
                  (update, not should_be_created, is_updateable, resource_json))

        try:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = True
            deploy_func = template_deployer.update_resource if update else template_deployer.deploy_resource
            result = deploy_func(logical_id, resource_map_new, stack_name=stack_name)
        finally:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = False

        if not should_be_created:
            # skip the parts below for update requests
            return resource

        def find_id(resource):
            """ Find ID of the given resource. """
            if not resource:
                return
            for id_attr in ('Id', 'id', 'ResourceId', 'RestApiId', 'DeploymentId', 'RoleId'):
                if id_attr in resource:
                    return resource[id_attr]

        # update resource IDs to avoid mismatch between CF moto and LocalStack backend resources
        if hasattr(resource, 'id') or (isinstance(resource, dict) and resource.get('id')):
            existing_id = resource.id if hasattr(resource, 'id') else resource['id']
            new_res_id = find_id(result)
            LOG.debug('Updating resource id: %s - %s, %s - %s' % (existing_id, new_res_id, resource, resource_json))
            if new_res_id:
                LOG.info('Updating resource ID from %s to %s (%s)' % (existing_id, new_res_id, region_name))
                update_resource_id(resource, new_res_id, props,
                    region_name, stack_name, resources_map._resource_json_map)
            else:
                LOG.warning('Unable to extract id for resource %s: %s' % (logical_id, result))

        # update physical_resource_id field
        update_physical_resource_id(resource)

        return resource