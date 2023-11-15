def create(vm_):
    '''
    Create a single VM from a data dict

    CLI Example:

    .. code-block:: bash

        salt-cloud -p profile_name vm_name
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                                           __active_provider_name__ or 'joyent',
                                                           vm_['profile'],
                                                           vm_=vm_) is False:
            return False
    except AttributeError:
        pass

    # Since using "provider: <provider-engine>" is deprecated, alias provider
    # to use driver: "driver: <provider-engine>"
    if 'provider' in vm_:
        vm_['driver'] = vm_.pop('provider')

    key_filename = config.get_cloud_config_value(
        'private_key', vm_, __opts__, search_global=False, default=None
    )

    salt.utils.cloud.fire_event(
        'event',
        'starting create',
        'salt/cloud/{0}/creating'.format(vm_['name']),
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['driver'],
        },
        transport=__opts__['transport']
    )

    log.info(
        'Creating Cloud VM {0} in {1}'.format(
            vm_['name'],
            vm_.get('location', DEFAULT_LOCATION)
        )
    )

    # added . for fqdn hostnames
    salt.utils.cloud.check_name(vm_['name'], 'a-zA-Z0-9-.')
    kwargs = {
        'name': vm_['name'],
        'image': get_image(vm_),
        'size': get_size(vm_),
        'location': vm_.get('location', DEFAULT_LOCATION)
    }
    # Let's not assign a default here; only assign a network value if
    # one is explicitly configured
    if 'networks' in vm_:
        kwargs['networks'] = vm_.get('networks')

    salt.utils.cloud.fire_event(
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        {'kwargs': kwargs},
        transport=__opts__['transport']
    )

    try:
        data = create_node(**kwargs)
    except Exception as exc:
        log.error(
            'Error creating {0} on JOYENT\n\n'
            'The following exception was thrown when trying to '
            'run the initial deployment: \n{1}'.format(
                vm_['name'], str(exc)
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return False

    query_instance(vm_)
    data = show_instance(vm_['name'], call='action')

    vm_['key_filename'] = key_filename
    vm_['ssh_host'] = data[1]['primaryIp']

    salt.utils.cloud.bootstrap(vm_, __opts__)

    salt.utils.cloud.fire_event(
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['driver'],
        },
        transport=__opts__['transport']
    )

    return data[1]