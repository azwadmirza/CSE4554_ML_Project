def deploy_template(template, stack_name):
    if isinstance(template, string_types):
        template = parse_template(template)

    if MARKER_DONT_REDEPLOY_STACK in template:
        # If we are currently deploying, then bail. This can occur if
        # deploy_template(..) method calls boto's update_stack(..) (to update the
        # state of resources) which itself triggers another call to deploy_template(..).
        # We don't want to end up in an infinite/recursive deployment loop.
        return

    resource_map = template.get('Resources')
    if not resource_map:
        LOGGER.warning('CloudFormation template contains no Resources section')
        return

    next = resource_map

    # resource_list = resource_map.values()
    iters = 3
    for i in range(0, iters):

        # print('deployment iteration', i)
        # get resource details
        for resource_id, resource in iteritems(next):
            resource['__details__'] = describe_stack_resources(stack_name, resource_id)[0]

        next = resources_to_deploy_next(resource_map, stack_name)
        if not next:
            return

        for resource_id, resource in iteritems(next):
            deploy_resource(resource_id, resource_map, stack_name=stack_name)

    LOGGER.warning('Unable to resolve all dependencies and deploy all resources ' +
        'after %s iterations. Remaining (%s): %s' % (iters, len(next), next))