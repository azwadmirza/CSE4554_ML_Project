def create(vm_):
    '''
    Create a single VM from a data dict
    '''

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

    log.info('Creating Cloud VM {0}'.format(vm_['name']))
    conn = get_conn()

    ssh_username = config.get_cloud_config_value(
        'ssh_username', vm_, __opts__, default='root'
    )
    if 'clonefrom' in vm_:
        if HAS_LIBCLOUD:
            if 'clonefrom' in vm_:
                log.error('Error: Linode via Apache Libcloud cannot clone.')
                return False

        clonesource = get_node(name=vm_['clonefrom'])

        kwargs = {
            'name': vm_['name'],
            'clonefrom': vm_['clonefrom'],
            'image': 'Clone of {0}'.format(vm_['clonefrom']),
            'size': clonesource['size'],
            'auth': get_auth(vm_),
            'ex_private': get_private_ip(vm_),
        }

        node_data = clone(vm_['clonefrom'], {'target': vm_['name']})

        salt.utils.cloud.fire_event(
            'event',
            'requesting instance',
            'salt/cloud/{0}/requesting'.format(vm_['name']),
            {'kwargs': {'name': kwargs['name'],
                        'image': kwargs['image'],
                        'size': kwargs['size'],
                        'ex_private': kwargs['ex_private']}},
            transport=__opts__['transport']
        )
    else:
        if HAS_LIBCLOUD:
            kwargs = {
                'name': vm_['name'],
                'image': get_image(conn, vm_),
                'size': get_size(conn, vm_),
                'location': get_location(conn, vm_),
                'auth': get_auth(vm_),
                'ex_private': get_private_ip(vm_),
                'ex_rsize': get_disk_size(vm_, get_size(conn, vm_), get_swap(vm_)),
                'ex_swap': get_swap(vm_)
            }

            salt.utils.cloud.fire_event(
                'event',
                'requesting instance',
                'salt/cloud/{0}/requesting'.format(vm_['name']),
                {'kwargs': {'name': kwargs['name'],
                                'image': kwargs['image'].name,
                                'size': kwargs['size'].name,
                                'location': kwargs['location'].name,
                                'ex_private': kwargs['ex_private'],
                                'ex_rsize': kwargs['ex_rsize'],
                                'ex_swap': kwargs['ex_swap']}},
                    transport=__opts__['transport']
                )

        if HAS_LINODEPY:
            kwargs = {
                'name': vm_['name'],
                'image': get_image(conn, vm_),
                'size': get_size(conn, vm_),
                'location': get_location(conn, vm_),
                'auth': get_auth(vm_),
                'ex_private': get_private_ip(vm_),
                'ex_rsize': get_disk_size(vm_, get_size(conn, vm_), get_swap(vm_)),
                'ex_swap': get_swap(vm_)
            }

            salt.utils.cloud.fire_event(
                'event',
                'requesting instance',
                'salt/cloud/{0}/requesting'.format(vm_['name']),
                {'kwargs': {'name': kwargs['name'],
                                'image': kwargs['image'],
                                'size': kwargs['size'],
                                'location': kwargs['location'],
                                'ex_private': kwargs['ex_private'],
                                'ex_rsize': kwargs['ex_rsize'],
                                'ex_swap': kwargs['ex_swap']}},
                    transport=__opts__['transport']
                )

        if 'libcloud_args' in vm_:
            kwargs.update(vm_['libcloud_args'])

        if HAS_LIBCLOUD:
            try:
                node_data = conn.create_node(**kwargs)
            except Exception as exc:
                log.error(
                    'Error creating {0} on Linode via Apache Libcloud\n\n'
                    'The following exception was thrown by libcloud when trying to '
                    'run the initial deployment: \n{1}'.format(
                        vm_['name'], str(exc)
                    ),
                    # Show the traceback if the debug logging level is enabled
                    exc_info_on_loglevel=logging.DEBUG
                )
                return False

        if HAS_LINODEPY:
            # linode-python version
            try:
                node_data = conn.linode_create(DatacenterID=get_location(conn, vm_),
                                               PlanID=kwargs['size']['extra']['PLANID'], PaymentTerm=1)
            except Exception as exc:
                log.error(
                    'Error creating {0} on Linode via linode-python\n\n'
                    'The following exception was thrown by linode-python when trying to '
                    'run the initial deployment: \n{1}'.format(
                        vm_['name'], str(exc)
                    ),
                    # Show the traceback if the debug logging level is enabled
                    exc_info_on_loglevel=logging.DEBUG
                )
                return False

            if not waitfor_status(conn=conn, LinodeID=node_data['LinodeID'], status='Brand New'):
                log.error('Error creating {0} on LINODE\n\n'
                    'while waiting for initial ready status'.format(
                        vm_['name']
                    ),
                    # Show the traceback if the debug logging level is enabled
                    exc_info_on_loglevel=logging.DEBUG
                )

            # Set linode name
            set_name_result = conn.linode_update(LinodeID=node_data['LinodeID'],
                                                 Label=vm_['name'])
            log.debug('Set name action for {0} was {1}'.format(vm_['name'],
                                                              set_name_result))

            # Create disks
            log.debug('Creating disks for {0}'.format(node_data['LinodeID']))
            swap_result = create_swap_disk(LinodeID=node_data['LinodeID'], swapsize=get_swap(vm_))

            root_result = create_disk_from_distro(vm_, LinodeID=node_data['LinodeID'],
                                                 swapsize=get_swap(vm_))

            # Create config
            config_result = create_config(vm_, LinodeID=node_data['LinodeID'],
                                          root_disk_id=root_result['DiskID'],
                                          swap_disk_id=swap_result['DiskID'])

            # Boot!
            boot_result = boot(LinodeID=node_data['LinodeID'],
                               configid=config_result['ConfigID'])

            if not waitfor_job(conn, LinodeID=node_data['LinodeID'],
                               JobID=boot_result['JobID']):
                log.error('Boot failed for {0}.'.format(node_data))
                return False

            node_data.update(get_node(node_data['LinodeID']))

    if HAS_LINODEPY:
        if get_private_ip(vm_) and config.get_cloud_config_value(
                                             'ssh_interface',
                                             get_configured_provider(),
                                             __opts__, search_global=False,
                                             default='public') == 'private':
            vm_['ssh_host'] = node_data['private_ips'][0]
        else:
            vm_['ssh_host'] = node_data['public_ips'][0]

    if HAS_LIBCLOUD:
        if get_private_ip(vm_) and config.get_cloud_config_value(
                                             'ssh_interface',
                                             get_configured_provider(),
                                             __opts__, search_global=False,
                                             default='public') == 'private':
            vm_['ssh_host'] = node_data.private_ips[0]
        else:
            vm_['ssh_host'] = node_data.public_ips[0]

    # If a password wasn't supplied in the profile or provider config, set it now.
    vm_['password'] = get_password(vm_)

    # Bootstrap, either apache-libcloud or linode-python
    ret = salt.utils.cloud.bootstrap(vm_, __opts__)

    if HAS_LINODEPY:
        ret.update(node_data)

    if HAS_LIBCLOUD:
        ret.update(node_data.__dict__)

    log.info('Created Cloud VM {0[name]!r}'.format(vm_))
    log.debug(
        '{0[name]!r} VM creation details:\n{1}'.format(
        vm_, pprint.pformat(node_data)
            )
    )

    salt.utils.cloud.fire_event(
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        {
            'name': vm_['name'],
            'profile': vm_['profile'],
            'provider': vm_['provider'],
        },
        transport=__opts__['transport']
    )

    return ret