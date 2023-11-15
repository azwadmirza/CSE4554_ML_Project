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

    # Since using "provider: <provider-engine>" is deprecated, alias provider
    # to use driver: "driver: <provider-engine>"
    if 'provider' in vm_:
        vm_['driver'] = vm_.pop('provider')

    __utils__['cloud.fire_event'](
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

    log.info('Creating Cloud VM %s', vm_['name'])
    conn = get_conn()
    rootPw = NodeAuthPassword(vm_['auth'])

    try:
        location = conn.ex_get_location_by_id(vm_['location'])
        images = conn.list_images(location=location)
        image = [x for x in images if x.id == vm_['image']][0]
        networks = conn.ex_list_network_domains(location=location)
        network_domain = [y for y in networks if y.name ==
                          vm_['network_domain']][0]
        # Use the first VLAN in the network domain
        vlan = conn.ex_list_vlans(location=location,
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

    def __query_node_data(vm_, data):
        running = False
        try:
            node = show_instance(vm_['name'], 'action')
            running = (node['state'] == NodeState.RUNNING)
            log.debug(
                'Loaded node data for %s:\nname: %s\nstate: %s',
                vm_['name'],
                pprint.pformat(node['name']),
                node['state']
                )
        except Exception as err:
            log.error(
                'Failed to get nodes list: %s', err,
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            # Trigger a failure in the wait for IP function
            return False

        if not running:
            # Still not running, trigger another iteration
            return

        private = node['private_ips']
        public = node['public_ips']

        if private and not public:
            log.warning(
                'Private IPs returned, but not public... Checking for '
                'misidentified IPs'
            )
            for private_ip in private:
                private_ip = preferred_ip(vm_, [private_ip])
                if private_ip is False:
                    continue
                if salt.utils.cloud.is_public_ip(private_ip):
                    log.warning('%s is a public IP', private_ip)
                    data.public_ips.append(private_ip)
                else:
                    log.warning('%s is a private IP', private_ip)
                    if private_ip not in data.private_ips:
                        data.private_ips.append(private_ip)

            if ssh_interface(vm_) == 'private_ips' and data.private_ips:
                return data

        if private:
            data.private_ips = private
            if ssh_interface(vm_) == 'private_ips':
                return data

        if public:
            data.public_ips = public
            if ssh_interface(vm_) != 'private_ips':
                return data

        log.debug('DATA')
        log.debug(data)

    try:
        data = salt.utils.cloud.wait_for_ip(
            __query_node_data,
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
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['driver'],
        },
        transport=__opts__['transport']
    )

    return ret