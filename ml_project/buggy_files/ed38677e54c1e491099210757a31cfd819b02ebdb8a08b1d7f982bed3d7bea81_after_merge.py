def update(name, launch_config_name, availability_zones, min_size, max_size,
           desired_capacity=None, load_balancers=None, default_cooldown=None,
           health_check_type=None, health_check_period=None,
           placement_group=None, vpc_zone_identifier=None, tags=None,
           termination_policies=None, suspended_processes=None,
           scaling_policies=None,
           region=None, key=None, keyid=None,
           profile=None):
    '''
    Update an autoscale group.

    CLI example::

        salt myminion boto_asg.update myasg mylc '["us-east-1a", "us-east-1e"]' 1 10 load_balancers='["myelb", "myelb2"]' tags='[{"key": "Name", value="myasg", "propagate_at_launch": True}]'
    '''

    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    if isinstance(availability_zones, string_types):
        availability_zones = json.loads(availability_zones)
    if isinstance(load_balancers, string_types):
        load_balancers = json.loads(load_balancers)
    if isinstance(vpc_zone_identifier, string_types):
        vpc_zone_identifier = json.loads(vpc_zone_identifier)
    if isinstance(tags, string_types):
        tags = json.loads(tags)
    # Make a list of tag objects from the dict.
    _tags = []
    if tags:
        for tag in tags:
            try:
                key = tag.get('key')
            except KeyError:
                log.error('Tag missing key.')
                return False
            try:
                value = tag.get('value')
            except KeyError:
                log.error('Tag missing value.')
                return False
            propagate_at_launch = tag.get('propagate_at_launch', False)
            _tag = autoscale.Tag(key=key, value=value, resource_id=name,
                                 propagate_at_launch=propagate_at_launch)
            _tags.append(_tag)
    if isinstance(termination_policies, string_types):
        termination_policies = json.loads(termination_policies)
    if isinstance(suspended_processes, string_types):
        suspended_processes = json.loads(suspended_processes)
    try:
        _asg = autoscale.AutoScalingGroup(
            connection=conn,
            name=name, launch_config=launch_config_name,
            availability_zones=availability_zones,
            min_size=min_size, max_size=max_size,
            desired_capacity=desired_capacity, load_balancers=load_balancers,
            default_cooldown=default_cooldown,
            health_check_type=health_check_type,
            health_check_period=health_check_period,
            placement_group=placement_group, tags=_tags,
            vpc_zone_identifier=vpc_zone_identifier,
            termination_policies=termination_policies)
        _asg.update()
        # Seems the update call doesn't handle tags, so we'll need to update
        # that separately.
        if _tags:
            conn.create_or_update_tags(_tags)
        # update doesn't handle suspended_processes either
        # Resume all processes
        _asg.resume_processes()
        # suspend any that are specified. Note that the boto default of empty
        # list suspends all; don't do that.
        if suspended_processes is not None and len(suspended_processes) > 0:
            _asg.suspend_processes(suspended_processes)
        log.info('Updated ASG {0}'.format(name))
        #### scaling policies
        # delete all policies, then recreate them
        for policy in conn.get_all_policies(as_group=name):
            conn.delete_policy(policy.name, autoscale_group=name)
        _create_scaling_policies(conn, name, scaling_policies)
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to update ASG {0}'.format(name)
        log.error(msg)
        return False