def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(
                __opts__,
                __active_provider_name__ or 'dimensiondata',
                vm_['profile']) is False:
            return False
    except AttributeError:
        pass

    __utils__['cloud.fire_event'](
        'event',
        'starting create',
        'salt/cloud/{0}/creating'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('creating', vm_, ['name', 'profile', 'provider', 'driver']),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    log.info('Creating Cloud VM %s', vm_['name'])
    conn = get_conn()
    rootPw = NodeAuthPassword(vm_['auth'])

    location = conn.ex_get_location_by_id(vm_['location'])
    images = conn.list_images(location=location)
    image = [x for x in images if x.id == vm_['image']][0]
    network_domains = conn.ex_list_network_domains(location=location)
    try:
        network_domain = [y for y in network_domains
                          if y.name == vm_['network_domain']][0]
    except IndexError:
        network_domain = conn.ex_create_network_domain(
            location=location,
            name=vm_['network_domain'],
            plan='ADVANCED',
            description=''
        )

    try:
        vlan = [y for y in conn.ex_list_vlans(
            location=location,
            network_domain=network_domain)
                if y.name == vm_['vlan']][0]
    except (IndexError, KeyError):
        # Use the first VLAN in the network domain
        vlan = conn.ex_list_vlans(
            location=location,
            network_domain=network_domain)[0]

    kwargs = {
        'name': vm_['name'],
        'image': image,
        'auth': rootPw,
        'ex_description': vm_['description'],
        'ex_network_domain': network_domain,
        'ex_vlan': vlan,
        'ex_is_started': vm_['is_started']
    }

    event_data = kwargs.copy()
    del event_data['auth']

    __utils__['cloud.fire_event'](
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('requesting', event_data, list(event_data)),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    try:
        data = conn.create_node(**kwargs)
    except Exception as exc:
        log.error(
            'Error creating %s on DIMENSIONDATA\n\n'
            'The following exception was thrown by libcloud when trying to '
            'run the initial deployment: \n%s',
            vm_['name'], exc,
            exc_info_on_loglevel=logging.DEBUG
        )
        return False

    try:
        data = salt.utils.cloud.wait_for_ip(
            _query_node_data,
            update_args=(vm_, data),
            timeout=config.get_cloud_config_value(
                'wait_for_ip_timeout', vm_, __opts__, default=25 * 60),
            interval=config.get_cloud_config_value(
                'wait_for_ip_interval', vm_, __opts__, default=30),
            max_failures=config.get_cloud_config_value(
                'wait_for_ip_max_failures', vm_, __opts__, default=60),
        )
    except (SaltCloudExecutionTimeout, SaltCloudExecutionFailure) as exc:
        try:
            # It might be already up, let's destroy it!
            destroy(vm_['name'])
        except SaltCloudSystemExit:
            pass
        finally:
            raise SaltCloudSystemExit(str(exc))

    log.debug('VM is now running')
    if ssh_interface(vm_) == 'private_ips':
        ip_address = preferred_ip(vm_, data.private_ips)
    else:
        ip_address = preferred_ip(vm_, data.public_ips)
    log.debug('Using IP address %s', ip_address)

    if salt.utils.cloud.get_salt_interface(vm_, __opts__) == 'private_ips':
        salt_ip_address = preferred_ip(vm_, data.private_ips)
        log.info('Salt interface set to: %s', salt_ip_address)
    else:
        salt_ip_address = preferred_ip(vm_, data.public_ips)
        log.debug('Salt interface set to: %s', salt_ip_address)

    if not ip_address:
        raise SaltCloudSystemExit(
            'No IP addresses could be found.'
        )

    vm_['salt_host'] = salt_ip_address
    vm_['ssh_host'] = ip_address
    vm_['password'] = vm_['auth']

    ret = salt.utils.cloud.bootstrap(vm_, __opts__)

    ret.update(data.__dict__)

    if 'password' in data.extra:
        del data.extra['password']

    log.info('Created Cloud VM \'{0[name]}\''.format(vm_))
    log.debug(
        '\'{0[name]}\' VM creation details:\n{1}'.format(
            vm_, pprint.pformat(data.__dict__)
        )
    )

    __utils__['cloud.fire_event'](
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('created', vm_, ['name', 'profile', 'provider', 'driver']),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    return ret