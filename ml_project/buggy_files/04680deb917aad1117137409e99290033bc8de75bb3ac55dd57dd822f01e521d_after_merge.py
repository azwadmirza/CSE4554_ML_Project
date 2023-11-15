def create(vm_=None, call=None):
    '''
    Create a single VM from a data dict
    '''
    if call:
        raise SaltCloudSystemExit(
            'You cannot create an instance with -a or -f.'
        )

    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                                           __active_provider_name__ or 'ec2',
                                                           vm_['profile'],
                                                           vm_=vm_) is False:
            return False
    except AttributeError:
        pass

    # Check for private_key and keyfile name for bootstrapping new instances
    deploy = config.get_cloud_config_value(
        'deploy', vm_, __opts__, default=True
    )
    win_password = config.get_cloud_config_value(
        'win_password', vm_, __opts__, default=''
    )
    key_filename = config.get_cloud_config_value(
        'private_key', vm_, __opts__, search_global=False, default=None
    )
    if deploy:
        # The private_key and keyname settings are only needed for bootstrapping
        # new instances when deploy is True
        _validate_key_path_and_mode(key_filename)

    __utils__['cloud.fire_event'](
        'event',
        'starting create',
        'salt/cloud/{0}/creating'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('creating', vm_, ['name', 'profile', 'provider', 'driver']),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )
    __utils__['cloud.cachedir_index_add'](
        vm_['name'], vm_['profile'], 'ec2', vm_['driver']
    )

    vm_['key_filename'] = key_filename
    # wait_for_instance requires private_key
    vm_['private_key'] = key_filename

    # Get SSH Gateway config early to verify the private_key,
    # if used, exists or not. We don't want to deploy an instance
    # and not be able to access it via the gateway.
    vm_['gateway'] = get_ssh_gateway_config(vm_)

    location = get_location(vm_)
    vm_['location'] = location

    log.info('Creating Cloud VM {0} in {1}'.format(vm_['name'], location))
    vm_['usernames'] = salt.utils.cloud.ssh_usernames(
        vm_,
        __opts__,
        default_users=(
            'ec2-user',  # Amazon Linux, Fedora, RHEL; FreeBSD
            'centos',    # CentOS AMIs from AWS Marketplace
            'ubuntu',    # Ubuntu
            'admin',     # Debian GNU/Linux
            'bitnami',   # BitNami AMIs
            'root'       # Last resort, default user on RHEL 5, SUSE
        )
    )

    if 'instance_id' in vm_:
        # This was probably created via another process, and doesn't have
        # things like salt keys created yet, so let's create them now.
        if 'pub_key' not in vm_ and 'priv_key' not in vm_:
            log.debug('Generating minion keys for \'{0[name]}\''.format(vm_))
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
        if keyname(vm_) is None:
            raise SaltCloudSystemExit(
                'The required \'keyname\' configuration setting is missing from the '
                '\'ec2\' driver.'
            )

        data, vm_ = request_instance(vm_, location)

        # If data is a str, it's an error
        if isinstance(data, str):
            log.error('Error requesting instance: {0}'.format(data))
            return {}

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

    for value in six.itervalues(tags):
        if not isinstance(value, str):
            raise SaltCloudConfigError(
                '\'tag\' values must be strings. Try quoting the values. '
                'e.g. "2013-09-19T20:09:46Z".'
            )

    tags['Name'] = vm_['name']

    __utils__['cloud.fire_event'](
        'event',
        'setting tags',
        'salt/cloud/{0}/tagging'.format(vm_['name']),
        args={'tags': tags},
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    salt.utils.cloud.wait_for_fun(
        set_tags,
        timeout=30,
        name=vm_['name'],
        tags=tags,
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
        _update_enis(network_interfaces, data, vm_)

    # At this point, the node is created and tagged, and now needs to be
    # bootstrapped, once the necessary port is available.
    log.info('Created node {0}'.format(vm_['name']))

    instance = data[0]['instancesSet']['item']

    # Wait for the necessary port to become available to bootstrap
    if ssh_interface(vm_) == 'private_ips':
        ip_address = instance['privateIpAddress']
        log.info('Salt node data. Private_ip: {0}'.format(ip_address))
    else:
        ip_address = instance['ipAddress']
        log.info('Salt node data. Public_ip: {0}'.format(ip_address))
    vm_['ssh_host'] = ip_address

    if salt.utils.cloud.get_salt_interface(vm_, __opts__) == 'private_ips':
        salt_ip_address = instance['privateIpAddress']
        log.info('Salt interface set to: {0}'.format(salt_ip_address))
    else:
        salt_ip_address = instance['ipAddress']
        log.debug('Salt interface set to: {0}'.format(salt_ip_address))
    vm_['salt_host'] = salt_ip_address

    if deploy:
        display_ssh_output = config.get_cloud_config_value(
            'display_ssh_output', vm_, __opts__, default=True
        )

        vm_ = wait_for_instance(
            vm_, data, ip_address, display_ssh_output
        )

    # The instance is booted and accessible, let's Salt it!
    ret = instance.copy()

    # Get ANY defined volumes settings, merging data, in the following order
    # 1. VM config
    # 2. Profile config
    # 3. Global configuration
    volumes = config.get_cloud_config_value(
        'volumes', vm_, __opts__, search_global=True
    )
    if volumes:
        __utils__['cloud.fire_event'](
            'event',
            'attaching volumes',
            'salt/cloud/{0}/attaching_volumes'.format(vm_['name']),
            args={'volumes': volumes},
            sock_dir=__opts__['sock_dir'],
            transport=__opts__['transport']
        )

        log.info('Create and attach volumes to node {0}'.format(vm_['name']))
        created = create_attach_volumes(
            vm_['name'],
            {
                'volumes': volumes,
                'zone': ret['placement']['availabilityZone'],
                'instance_id': ret['instanceId'],
                'del_all_vols_on_destroy': vm_.get('del_all_vols_on_destroy', False)
            },
            call='action'
        )
        ret['Attached Volumes'] = created

    # Associate instance with a ssm document, if present
    ssm_document = config.get_cloud_config_value(
        'ssm_document', vm_, __opts__, None, search_global=False
    )
    if ssm_document:
        log.debug('Associating with ssm document: {0}'.format(ssm_document))
        assoc = ssm_create_association(
            vm_['name'],
            {'ssm_document': ssm_document},
            instance_id=vm_['instance_id'],
            call='action'
        )
        if isinstance(assoc, dict) and assoc.get('error', None):
            log.error('Failed to associate instance {0} with ssm document {1}'.format(
                vm_['instance_id'], ssm_document
            ))
            return {}

    for key, value in six.iteritems(__utils__['cloud.bootstrap'](vm_, __opts__)):
        ret.setdefault(key, value)

    log.info('Created Cloud VM \'{0[name]}\''.format(vm_))
    log.debug(
        '\'{0[name]}\' VM creation details:\n{1}'.format(
            vm_, pprint.pformat(instance)
        )
    )

    event_data = {
        'name': vm_['name'],
        'profile': vm_['profile'],
        'provider': vm_['driver'],
        'instance_id': vm_['instance_id'],
    }
    if volumes:
        event_data['volumes'] = volumes
    if ssm_document:
        event_data['ssm_document'] = ssm_document

    __utils__['cloud.fire_event'](
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('created', event_data, list(event_data)),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    # Ensure that the latest node data is returned
    node = _get_node(instance_id=vm_['instance_id'])
    ret.update(node)

    return ret