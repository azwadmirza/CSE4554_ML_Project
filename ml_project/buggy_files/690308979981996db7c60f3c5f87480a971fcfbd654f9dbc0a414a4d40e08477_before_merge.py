def create(vm_=None, call=None):
    '''
    Create a single VM from a data dict
    '''
    if call:
        raise SaltCloudSystemExit(
            'You cannot create an instance with -a or -f.'
        )

    salt.utils.cloud.fire_event(
        'event',
        'starting create',
        'salt/cloud/{0}/creating'.format(vm_['name']),
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['provider'],
        },
        transport=__opts__['transport']
    )

    key_filename = config.get_cloud_config_value(
        'private_key', vm_, __opts__, search_global=False, default=None
    )
    if key_filename is not None and not os.path.isfile(key_filename):
        raise SaltCloudConfigError(
            'The defined key_filename {0!r} does not exist'.format(
                key_filename
            )
        )
    vm_['key_filename'] = key_filename

    # Get SSH Gateway config early to verify the private_key,
    # if used, exists or not. We don't want to deploy an instance
    # and not be able to access it via the gateway.
    ssh_gateway_config = get_ssh_gateway_config(vm_)
    vm_['ssh_gateway_config'] = ssh_gateway_config

    location = get_location(vm_)
    vm_['location'] = location

    log.info('Creating Cloud VM {0} in {1}'.format(vm_['name'], location))
    vm_['usernames'] = salt.utils.cloud.ssh_usernames(
        vm_,
        __opts__,
        default_users=(
            'ec2-user', 'ubuntu', 'fedora', 'admin', 'bitnami', 'root'
        )
    )

    if 'instance_id' in vm_:
        # This was probably created via another process, and doesn't have
        # things like salt keys created yet, so let's create them now.
        if 'pub_key' not in vm_ and 'priv_key' not in vm_:
            log.debug('Generating minion keys for {0[name]!r}'.format(vm_))
            vm_['priv_key'], vm_['pub_key'] = salt.utils.cloud.gen_keys(
                salt.config.get_cloud_config_value(
                    'keysize',
                    vm_,
                    __opts__
                )
            )
    else:
        # Put together all of the information required to request the instance,
        # and then fire off the request for it
        data, vm_ = request_instance(vm_, location)

        # Pull the instance ID, valid for both spot and normal instances

        # Multiple instances may have been spun up, get all their IDs
        vm_['instance_id_list'] = []
        for instance in data:
            vm_['instance_id_list'].append(instance['instanceId'])

        vm_['instance_id'] = vm_['instance_id_list'].pop()
        if len(vm_['instance_id_list']) > 0:
            # Multiple instances were spun up, get one now, and queue the rest
            queue_instances(vm_['instance_id_list'])

    # Wait for vital information, such as IP addresses, to be available
    # for the new instance
    data = query_instance(vm_)

    # Now that the instance is available, tag it appropriately. Should
    # mitigate race conditions with tags
    tags = config.get_cloud_config_value('tag',
                                         vm_,
                                         __opts__,
                                         {},
                                         search_global=False)
    if not isinstance(tags, dict):
        raise SaltCloudConfigError(
            '\'tag\' should be a dict.'
        )

    for value in tags.values():
        if not isinstance(value, str):
            raise SaltCloudConfigError(
                '\'tag\' values must be strings. Try quoting the values. '
                'e.g. "2013-09-19T20:09:46Z".'
            )

    tags['Name'] = vm_['name']

    salt.utils.cloud.fire_event(
        'event',
        'setting tags',
        'salt/cloud/{0}/tagging'.format(vm_['name']),
        {'tags': tags},
        transport=__opts__['transport']
    )

    set_tags(
        vm_['name'],
        tags,
        instance_id=vm_['instance_id'],
        call='action',
        location=location
    )

    network_interfaces = config.get_cloud_config_value(
        'network_interfaces',
        vm_,
        __opts__,
        search_global=False
    )

    if network_interfaces:
        _update_enis(network_interfaces, data)

    # At this point, the node is created and tagged, and now needs to be
    # bootstrapped, once the necessary port is available.
    log.info('Created node {0}'.format(vm_['name']))

    # Wait for the necessary port to become available to bootstrap
    if ssh_interface(vm_) == 'private_ips':
        ip_address = data[0]['instancesSet']['item']['privateIpAddress']
        log.info('Salt node data. Private_ip: {0}'.format(ip_address))
    else:
        ip_address = data[0]['instancesSet']['item']['ipAddress']
        log.info('Salt node data. Public_ip: {0}'.format(ip_address))
    vm_['ssh_host'] = ip_address

    display_ssh_output = config.get_cloud_config_value(
        'display_ssh_output', vm_, __opts__, default=True
    )

    vm_ = wait_for_instance(
        vm_, data, ip_address, display_ssh_output
    )

    # The instance is booted and accessable, let's Salt it!
    ret = salt.utils.cloud.bootstrap(vm_, __opts__)

    log.info('Created Cloud VM {0[name]!r}'.format(vm_))
    log.debug(
        '{0[name]!r} VM creation details:\n{1}'.format(
            vm_, pprint.pformat(data[0]['instancesSet']['item'])
        )
    )

    ret.update(data[0]['instancesSet']['item'])

    # Get ANY defined volumes settings, merging data, in the following order
    # 1. VM config
    # 2. Profile config
    # 3. Global configuration
    volumes = config.get_cloud_config_value(
        'volumes', vm_, __opts__, search_global=True
    )
    if volumes:
        salt.utils.cloud.fire_event(
            'event',
            'attaching volumes',
            'salt/cloud/{0}/attaching_volumes'.format(vm_['name']),
            {'volumes': volumes},
            transport=__opts__['transport']
        )

        log.info('Create and attach volumes to node {0}'.format(vm_['name']))
        created = create_attach_volumes(
            vm_['name'],
            {
                'volumes': volumes,
                'zone': ret['placement']['availabilityZone'],
                'instance_id': ret['instanceId'],
                'del_all_vols_on_destroy': vm_.get('set_del_all_vols_on_destroy', False)
            },
            call='action'
        )
        ret['Attached Volumes'] = created

    salt.utils.cloud.fire_event(
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['provider'],
            'instance_id': vm_['instance_id'],
        },
        transport=__opts__['transport']
    )

    return ret