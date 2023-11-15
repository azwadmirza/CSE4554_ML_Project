def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                                           __active_provider_name__ or 'digital_ocean',
                                                           vm_['profile'],
                                                           vm_=vm_) is False:
            return False
    except AttributeError:
        pass

    # Since using "provider: <provider-engine>" is deprecated, alias provider
    # to use driver: "driver: <provider-engine>"
    if 'provider' in vm_:
        vm_['driver'] = vm_.pop('provider')

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

    log.info('Creating Cloud VM {0}'.format(vm_['name']))

    kwargs = {
        'name': vm_['name'],
        'size': get_size(vm_),
        'image': get_image(vm_),
        'region': get_location(vm_),
        'ssh_keys': []
    }

    # backwards compat
    ssh_key_name = config.get_cloud_config_value(
        'ssh_key_name', vm_, __opts__, search_global=False
    )

    if ssh_key_name:
        kwargs['ssh_keys'].append(get_keyid(ssh_key_name))

    ssh_key_names = config.get_cloud_config_value(
        'ssh_key_names', vm_, __opts__, search_global=False, default=False
    )

    if ssh_key_names:
        for key in ssh_key_names.split(','):
            kwargs['ssh_keys'].append(get_keyid(key))

    key_filename = config.get_cloud_config_value(
        'ssh_key_file', vm_, __opts__, search_global=False, default=None
    )

    if key_filename is not None and not os.path.isfile(key_filename):
        raise SaltCloudConfigError(
            'The defined key_filename \'{0}\' does not exist'.format(
                key_filename
            )
        )

    if key_filename is None:
        raise SaltCloudConfigError(
            'The DigitalOcean driver requires an ssh_key_file and an ssh_key_name '
            'because it does not supply a root password upon building the server.'
        )

    private_networking = config.get_cloud_config_value(
        'private_networking', vm_, __opts__, search_global=False, default=None,
    )

    if private_networking is not None:
        if not isinstance(private_networking, bool):
            raise SaltCloudConfigError("'private_networking' should be a boolean value.")
        kwargs['private_networking'] = private_networking

    backups_enabled = config.get_cloud_config_value(
        'backups_enabled', vm_, __opts__, search_global=False, default=None,
    )

    if backups_enabled is not None:
        if not isinstance(backups_enabled, bool):
            raise SaltCloudConfigError("'backups_enabled' should be a boolean value.")
        kwargs['backups'] = backups_enabled

    ipv6 = config.get_cloud_config_value(
        'ipv6', vm_, __opts__, search_global=False, default=None,
    )

    if ipv6 is not None:
        if not isinstance(ipv6, bool):
            raise SaltCloudConfigError("'ipv6' should be a boolean value.")
        kwargs['ipv6'] = ipv6

    create_dns_record = config.get_cloud_config_value(
        'create_dns_record', vm_, __opts__, search_global=False, default=None,
    )

    if create_dns_record:
        log.info('create_dns_record: will attempt to write DNS records')
        default_dns_domain = None
        dns_domain_name = vm_['name'].split('.')
        if len(dns_domain_name) > 2:
            log.debug('create_dns_record: inferring default dns_hostname, dns_domain from minion name as FQDN')
            default_dns_hostname = '.'.join(dns_domain_name[:-2])
            default_dns_domain = '.'.join(dns_domain_name[-2:])
        else:
            log.debug("create_dns_record: can't infer dns_domain from {0}".format(vm_['name']))
            default_dns_hostname = dns_domain_name[0]

        dns_hostname = config.get_cloud_config_value(
            'dns_hostname', vm_, __opts__, search_global=False, default=default_dns_hostname,
        )
        dns_domain = config.get_cloud_config_value(
            'dns_domain', vm_, __opts__, search_global=False, default=default_dns_domain,
        )
        if dns_hostname and dns_domain:
            log.info('create_dns_record: using dns_hostname="{0}", dns_domain="{1}"'.format(dns_hostname, dns_domain))
            __add_dns_addr__ = lambda t, d: post_dns_record(dns_domain=dns_domain,
                                                            name=dns_hostname,
                                                            record_type=t,
                                                            record_data=d)

            log.debug('create_dns_record: {0}'.format(__add_dns_addr__))
        else:
            log.error('create_dns_record: could not determine dns_hostname and/or dns_domain')
            raise SaltCloudConfigError(
                '\'create_dns_record\' must be a dict specifying "domain" '
                'and "hostname" or the minion name must be an FQDN.'
            )

    salt.utils.cloud.fire_event(
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        {'kwargs': kwargs},
        transport=__opts__['transport']
    )

    try:
        ret = create_node(kwargs)
    except Exception as exc:
        log.error(
            'Error creating {0} on DIGITAL_OCEAN\n\n'
            'The following exception was thrown when trying to '
            'run the initial deployment: {1}'.format(
                vm_['name'],
                str(exc)
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return False

    def __query_node_data(vm_name):
        data = show_instance(vm_name, 'action')
        if not data:
            # Trigger an error in the wait_for_ip function
            return False
        if data['networks'].get('v4'):
            for network in data['networks']['v4']:
                if network['type'] == 'public':
                    return data
        return False

    try:
        data = salt.utils.cloud.wait_for_ip(
            __query_node_data,
            update_args=(vm_['name'],),
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

    if not vm_.get('ssh_host'):
        vm_['ssh_host'] = None

    # add DNS records, set ssh_host, default to first found IP, preferring IPv4 for ssh bootstrap script target
    addr_families, dns_arec_types = (('v4', 'v6'), ('A', 'AAAA'))
    arec_map = dict(list(zip(addr_families, dns_arec_types)))
    for facing, addr_family, ip_address in [(net['type'], family, net['ip_address'])
                                            for family in addr_families
                                            for net in data['networks'][family]]:
        log.info('found {0} IP{1} interface for "{2}"'.format(facing, addr_family, ip_address))
        dns_rec_type = arec_map[addr_family]
        if facing == 'public':
            if create_dns_record:
                __add_dns_addr__(dns_rec_type, ip_address)
            if not vm_['ssh_host']:
                vm_['ssh_host'] = ip_address

    if vm_['ssh_host'] is None:
        raise SaltCloudSystemExit(
            'No suitable IP addresses found for ssh minion bootstrapping: {0}'.format(repr(data['networks']))
        )

    log.debug('Found public IP address to use for ssh minion bootstrapping: {0}'.format(vm_['ssh_host']))

    vm_['key_filename'] = key_filename
    ret = salt.utils.cloud.bootstrap(vm_, __opts__)
    ret.update(data)

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