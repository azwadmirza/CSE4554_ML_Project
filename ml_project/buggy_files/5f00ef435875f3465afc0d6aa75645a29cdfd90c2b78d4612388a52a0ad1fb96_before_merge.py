def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    if 'driver' not in vm_:
        vm_['driver'] = vm_['provider']

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

    osid = _lookup_vultrid(vm_['image'], 'avail_images', 'OSID')
    if not osid:
        log.error('Vultr does not have an image with id or name {0}'.format(vm_['image']))
        return False

    vpsplanid = _lookup_vultrid(vm_['size'], 'avail_sizes', 'VPSPLANID')
    if not vpsplanid:
        log.error('Vultr does not have a size with id or name {0}'.format(vm_['size']))
        return False

    dcid = _lookup_vultrid(vm_['location'], 'avail_locations', 'DCID')
    if not dcid:
        log.error('Vultr does not have a location with id or name {0}'.format(vm_['location']))
        return False

    kwargs = {
        'label': vm_['name'],
        'OSID': osid,
        'VPSPLANID': vpsplanid,
        'DCID': dcid,
    }

    log.info('Creating Cloud VM {0}'.format(vm_['name']))

    salt.utils.cloud.fire_event(
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        {'kwargs': kwargs},
        transport=__opts__['transport'],
    )

    try:
        data = _query('server/create', method='POST', data=kwargs)
        if int(data.get('status', '200')) >= 300:
            log.error('Error creating {0} on Vultr\n\n'
                'Vultr API returned {1}\n'.format(vm_['name'], data))
            log.error('Status 412 may mean that you are requesting an\n'
                      'invalid location, image, or size.')

            salt.utils.cloud.fire_event(
                'event',
                'instance request failed',
                'salt/cloud/{0}/requesting/failed'.format(vm_['name']),
                {'kwargs': kwargs},
                transport=__opts__['transport'],
            )
            return False
    except Exception as exc:
        log.error(
            'Error creating {0} on Vultr\n\n'
            'The following exception was thrown when trying to '
            'run the initial deployment: \n{1}'.format(
                vm_['name'], str(exc)
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        salt.utils.cloud.fire_event(
            'event',
            'instance request failed',
            'salt/cloud/{0}/requesting/failed'.format(vm_['name']),
            {'kwargs': kwargs},
            transport=__opts__['transport'],
        )
        return False

    def wait_for_hostname():
        '''
        Wait for the IP address to become available
        '''
        data = show_instance(vm_['name'], call='action')
        pprint.pprint(data)
        if str(data.get('main_ip', '0')) == '0':
            time.sleep(3)
            return False
        return data['main_ip']

    def wait_for_default_password():
        '''
        Wait for the IP address to become available
        '''
        data = show_instance(vm_['name'], call='action')
        pprint.pprint(data)
        if str(data.get('default_password', '')) == '':
            time.sleep(1)
            return False
        if '!' not in data['default_password']:
            time.sleep(1)
            return False
        return data['default_password']

    vm_['ssh_host'] = salt.utils.cloud.wait_for_fun(
        wait_for_hostname,
        timeout=config.get_cloud_config_value(
            'wait_for_fun_timeout', vm_, __opts__, default=15 * 60),
    )
    vm_['password'] = salt.utils.cloud.wait_for_fun(
        wait_for_default_password,
        timeout=config.get_cloud_config_value(
            'wait_for_fun_timeout', vm_, __opts__, default=15 * 60),
    )
    __opts__['hard_timeout'] = config.get_cloud_config_value(
        'hard_timeout',
        get_configured_provider(),
        __opts__,
        search_global=False,
        default=15,
    )

    # Bootstrap
    ret = salt.utils.cloud.bootstrap(vm_, __opts__)

    ret.update(show_instance(vm_['name'], call='action'))

    log.info('Created Cloud VM \'{0[name]}\''.format(vm_))
    log.debug(
        '\'{0[name]}\' VM creation details:\n{1}'.format(
        vm_, pprint.pformat(data)
            )
    )

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

    return ret