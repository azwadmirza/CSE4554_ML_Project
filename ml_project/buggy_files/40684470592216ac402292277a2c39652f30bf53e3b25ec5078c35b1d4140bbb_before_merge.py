def create(vm_):
    '''
    Create a single Linode VM.
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                                           __active_provider_name__ or 'linode',
                                                           vm_['profile']) is False:
            return False
    except AttributeError:
        pass

    # Since using "provider: <provider-engine>" is deprecated, alias provider
    # to use driver: "driver: <provider-engine>"
    if 'provider' in vm_:
        vm_['driver'] = vm_.pop('provider')

    if _validate_name(vm_['name']) is False:
        return False

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

    data = {}
    kwargs = {
        'name': vm_['name'],
        'image': vm_['image'],
        'size': vm_['size'],
    }

    plan_id = get_plan_id(kwargs={'label': vm_['size']})
    try:
        datacenter_id = get_datacenter_id(vm_['location'])
    except KeyError:
        # Linode's default datacenter is Dallas, but we still have to set one to
        # use the create function from Linode's API. Dallas's datacenter id is 2.
        datacenter_id = 2

    if 'clonefrom' in vm_:
        linode_id = get_linode_id_from_name(vm_['clonefrom'])
        clone_source = get_linode(kwargs={'linode_id': linode_id})

        kwargs.update({'clonefrom': vm_['clonefrom']})
        kwargs['image'] = 'Clone of {0}'.format(vm_['clonefrom'])
        kwargs['size'] = clone_source['TOTALRAM']

        try:
            result = clone(kwargs={'linode_id': linode_id,
                                   'datacenter_id': datacenter_id,
                                   'plan_id': plan_id})
        except Exception:
            log.error(
                'Error cloning {0} on Linode\n\n'
                'The following exception was thrown by Linode when trying to '
                'clone the specified machine:\n'.format(
                    vm_['clonefrom']
                ),
                exc_info_on_loglevel=logging.DEBUG
            )
            return False
    else:
        try:
            result = _query('linode', 'create', args={
                'PLANID': plan_id,
                'DATACENTERID': datacenter_id
            })
        except Exception:
            log.error(
                'Error creating {0} on Linode\n\n'
                'The following exception was thrown by Linode when trying to '
                'run the initial deployment:\n'.format(
                    vm_['name']
                ),
                exc_info_on_loglevel=logging.DEBUG
            )
            return False

    salt.utils.cloud.fire_event(
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        {'kwargs': kwargs},
        transport=__opts__['transport']
    )

    node_id = _clean_data(result)['LinodeID']
    data['id'] = node_id

    if not _wait_for_status(node_id, status=(_get_status_id_by_name('brand_new'))):
        log.error(
            'Error creating {0} on LINODE\n\n'
            'while waiting for initial ready status'.format(vm_['name']),
            exc_info_on_loglevel=logging.DEBUG
        )

    # Update the Linode's Label to reflect the given VM name
    update_linode(node_id, update_args={'Label': vm_['name']})
    log.debug('Set name for {0} - was linode{1}.'.format(vm_['name'], node_id))

    # Create disks and get ids
    log.debug('Creating disks for {0}'.format(vm_['name']))
    root_disk_id = create_disk_from_distro(vm_, node_id)['DiskID']
    swap_disk_id = create_swap_disk(vm_, node_id)['DiskID']

    # Add private IP address if requested
    if get_private_ip(vm_):
        create_private_ip(vm_, node_id)

    # Create a ConfigID using disk ids
    config_id = create_config(kwargs={'name': vm_['name'],
                                      'linode_id': node_id,
                                      'root_disk_id': root_disk_id,
                                      'swap_disk_id': swap_disk_id})['ConfigID']
    # Boot the Linode
    boot(kwargs={'linode_id': node_id,
                 'config_id': config_id,
                 'check_running': False})

    node_data = get_linode(kwargs={'linode_id': node_id})
    ips = get_ips(node_id)
    state = int(node_data['STATUS'])

    data['image'] = vm_['image']
    data['name'] = node_data['LABEL']
    data['size'] = node_data['TOTALRAM']
    data['state'] = _get_status_descr_by_id(state)
    data['private_ips'] = ips['private_ips']
    data['public_ips'] = ips['public_ips']

    vm_['ssh_host'] = data['public_ips'][0]

    # If a password wasn't supplied in the profile or provider config, set it now.
    vm_['password'] = get_password(vm_)

    # Bootstrap!
    ret = salt.utils.cloud.bootstrap(vm_, __opts__)

    ret.update(data)

    log.info('Created Cloud VM {0[name]!r}'.format(vm_))
    log.debug(
        '{0[name]!r} VM creation details:\n{1}'.format(
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