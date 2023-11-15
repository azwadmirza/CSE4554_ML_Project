def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                                           __active_provider_name__ or 'nova',
                                                           vm_['profile'],
                                                           vm_=vm_) is False:
            return False
    except AttributeError:
        pass

    deploy = config.get_cloud_config_value('deploy', vm_, __opts__)
    key_filename = config.get_cloud_config_value(
        'ssh_key_file', vm_, __opts__, search_global=False, default=None
    )
    if key_filename is not None and not os.path.isfile(key_filename):
        raise SaltCloudConfigError(
            'The defined ssh_key_file \'{0}\' does not exist'.format(
                key_filename
            )
        )

    vm_['key_filename'] = key_filename

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
    conn = get_conn()

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
        data = conn.server_show_libcloud(vm_['instance_id'])
        if vm_['key_filename'] is None and 'change_password' in __opts__ and __opts__['change_password'] is True:
            vm_['password'] = sup.secure_password()
            conn.root_password(vm_['instance_id'], vm_['password'])
    else:
        # Put together all of the information required to request the instance,
        # and then fire off the request for it
        data, vm_ = request_instance(vm_)

        # Pull the instance ID, valid for both spot and normal instances
        vm_['instance_id'] = data.id

    def __query_node_data(vm_, data):
        try:
            node = show_instance(vm_['name'], 'action')
            log.debug(
                'Loaded node data for {0}:\n{1}'.format(
                    vm_['name'],
                    pprint.pformat(node)
                )
            )
        except Exception as err:
            log.error(
                'Failed to get nodes list: {0}'.format(
                    err
                ),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            # Trigger a failure in the wait for IP function
            return False

        running = node['state'] == 'ACTIVE'
        if not running:
            # Still not running, trigger another iteration
            return

        if rackconnect(vm_) is True:
            extra = node.get('extra', {})
            rc_status = extra.get('metadata', {}).get(
                'rackconnect_automation_status', '')
            if rc_status != 'DEPLOYED':
                log.debug('Waiting for Rackconnect automation to complete')
                return

        if managedcloud(vm_) is True:
            extra = conn.server_show_libcloud(
                node['id']
            ).extra
            mc_status = extra.get('metadata', {}).get(
                'rax_service_level_automation', '')

            if mc_status != 'Complete':
                log.debug('Waiting for managed cloud automation to complete')
                return

        access_ip = node.get('extra', {}).get('access_ip', '')

        rcv3 = rackconnectv3(vm_) in node['addresses']
        sshif = ssh_interface(vm_) in node['addresses']

        if any((rcv3, sshif)):
            networkname = rackconnectv3(vm_) if rcv3 else ssh_interface(vm_)
            for network in node['addresses'].get(networkname, []):
                if network['version'] is 4:
                    access_ip = network['addr']
                    break
            vm_['cloudnetwork'] = True

        # Conditions to pass this
        #
        #     Rackconnect v2: vm_['rackconnect'] = True
        #         If this is True, then the server will not be accessible from the ipv4 addres in public_ips.
        #         That interface gets turned off, and an ipv4 from the dedicated firewall is routed to the
        #         server.  In this case we can use the private_ips for ssh_interface, or the access_ip.
        #
        #     Rackconnect v3: vm['rackconnectv3'] = <cloudnetwork>
        #         If this is the case, salt will need to use the cloud network to login to the server.  There
        #         is no ipv4 address automatically provisioned for these servers when they are booted.  SaltCloud
        #         also cannot use the private_ips, because that traffic is dropped at the hypervisor.
        #
        #     CloudNetwork: vm['cloudnetwork'] = True
        #         If this is True, then we should have an access_ip at this point set to the ip on the cloud
        #         network.  If that network does not exist in the 'addresses' dictionary, then SaltCloud will
        #         use the initial access_ip, and not overwrite anything.
        if any((cloudnetwork(vm_), rackconnect(vm_))) and (ssh_interface(vm_) != 'private_ips' or rcv3) and access_ip != '':
            data.public_ips = [access_ip, ]
            return data

        result = []

        if 'private_ips' not in node and 'public_ips' not in node and \
           'access_ip' in node.get('extra', {}):
            result = [node['extra']['access_ip']]

        private = node.get('private_ips', [])
        public = node.get('public_ips', [])
        if private and not public:
            log.warn(
                'Private IPs returned, but not public... Checking for '
                'misidentified IPs'
            )
            for private_ip in private:
                private_ip = preferred_ip(vm_, [private_ip])
                if private_ip is False:
                    continue
                if salt.utils.cloud.is_public_ip(private_ip):
                    log.warn('{0} is a public IP'.format(private_ip))
                    data.public_ips.append(private_ip)
                    log.warn(
                        (
                            'Public IP address was not ready when we last'
                            ' checked.  Appending public IP address now.'
                        )
                    )
                    public = data.public_ips
                else:
                    log.warn('{0} is a private IP'.format(private_ip))
                    ignore_ip = ignore_cidr(vm_, private_ip)
                    if private_ip not in data.private_ips and not ignore_ip:
                        result.append(private_ip)

        # populate return data with private_ips
        # when ssh_interface is set to private_ips and public_ips exist
        if not result and ssh_interface(vm_) == 'private_ips':
            for private_ip in private:
                ignore_ip = ignore_cidr(vm_, private_ip)
                if private_ip not in data.private_ips and not ignore_ip:
                    result.append(private_ip)

        if public:
            data.public_ips = public
            if ssh_interface(vm_) != 'private_ips':
                return data

        if result:
            log.debug('result = {0}'.format(result))
            data.private_ips = result
            if ssh_interface(vm_) == 'private_ips':
                return data

    try:
        data = salt.utils.cloud.wait_for_ip(
            __query_node_data,
            update_args=(vm_, data),
            timeout=config.get_cloud_config_value(
                'wait_for_ip_timeout', vm_, __opts__, default=10 * 60),
            interval=config.get_cloud_config_value(
                'wait_for_ip_interval', vm_, __opts__, default=10),
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
    log.debug('Using IP address {0}'.format(ip_address))

    if salt.utils.cloud.get_salt_interface(vm_, __opts__) == 'private_ips':
        salt_ip_address = preferred_ip(vm_, data.private_ips)
        log.info('Salt interface set to: {0}'.format(salt_ip_address))
    else:
        salt_ip_address = preferred_ip(vm_, data.public_ips)
        log.debug('Salt interface set to: {0}'.format(salt_ip_address))

    if not ip_address:
        raise SaltCloudSystemExit('A valid IP address was not found')

    vm_['ssh_host'] = ip_address
    vm_['salt_host'] = salt_ip_address

    ret = __utils__['cloud.bootstrap'](vm_, __opts__)

    ret.update(data.__dict__)

    if 'password' in ret['extra']:
        del ret['extra']['password']

    log.info('Created Cloud VM \'{0[name]}\''.format(vm_))
    log.debug(
        '\'{0[name]}\' VM creation details:\n{1}'.format(
            vm_, pprint.pformat(data)
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