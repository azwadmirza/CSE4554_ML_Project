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

    label = vm_.get('label', vm_['name'])
    service_kwargs = {
        'service_name': vm_['name'],
        'label': label,
        'description': vm_.get('desc', vm_['name']),
        'location': vm_['location'],
    }

    ssh_endpoint = azure.servicemanagement.ConfigurationSetInputEndpoint(
        name='SSH',
        protocol='TCP',
        port='22',
        local_port='22',
    )

    network_config = azure.servicemanagement.ConfigurationSet()
    network_config.input_endpoints.input_endpoints.append(ssh_endpoint)
    network_config.configuration_set_type = 'NetworkConfiguration'

    linux_config = azure.servicemanagement.LinuxConfigurationSet(
        host_name=vm_['name'],
        user_name=vm_['ssh_username'],
        user_password=vm_['ssh_password'],
        disable_ssh_password_authentication=False,
    )

    # TODO: Might need to create a storage account
    media_link = vm_['media_link']
    # TODO: Probably better to use more than just the name in the media_link
    media_link += '/{0}.vhd'.format(vm_['name'])
    os_hd = azure.servicemanagement.OSVirtualHardDisk(vm_['image'], media_link)

    vm_kwargs = {
        'service_name': vm_['name'],
        'deployment_name': vm_['name'],
        'deployment_slot': vm_['slot'],
        'label': label,
        'role_name': vm_['name'],
        'system_config': linux_config,
        'os_virtual_hard_disk': os_hd,
        'role_size': vm_['size'],
        'network_config': network_config,
    }
    log.debug('vm_kwargs: {0}'.format(vm_kwargs))

    event_kwargs = {'service_kwargs': service_kwargs.copy(),
                    'vm_kwargs': vm_kwargs.copy()}
    del event_kwargs['vm_kwargs']['system_config']
    del event_kwargs['vm_kwargs']['os_virtual_hard_disk']
    del event_kwargs['vm_kwargs']['network_config']
    salt.utils.cloud.fire_event(
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        event_kwargs,
        transport=__opts__['transport']
    )
    log.debug('vm_kwargs: {0}'.format(vm_kwargs))

    # Azure lets you open winrm on a new VM
    # Can open up specific ports in Azure; but not on Windows

    try:
        conn.create_hosted_service(**service_kwargs)
        conn.create_virtual_machine_deployment(**vm_kwargs)
    except Exception as exc:
        error = 'The hosted service name is invalid.'
        if error in str(exc):
            log.error(
                'Error creating {0} on Azure.\n\n'
                'The hosted service name is invalid. The name can contain '
                'only letters, numbers, and hyphens. The name must start with '
                'a letter and must end with a letter or a number.'.format(
                    vm_['name']
                ),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
        else:
            log.error(
                'Error creating {0} on Azure\n\n'
                'The following exception was thrown when trying to '
                'run the initial deployment: \n{1}'.format(
                    vm_['name'], str(exc)
                ),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
        return False

    def wait_for_hostname():
        '''
        Wait for the IP address to become available
        '''
        try:
            data = show_instance(vm_['name'], call='action')
        except Exception:
            pass
        if 'url' in data and data['url'] != str(''):
            return data['url']
        time.sleep(1)
        return False

    hostname = salt.utils.cloud.wait_for_fun(
        wait_for_hostname,
        timeout=config.get_cloud_config_value(
            'wait_for_fun_timeout', vm_, __opts__, default=15 * 60),
    )

    if not hostname:
        log.error('Failed to get a value for the hostname.')
        return False

    hostname = hostname.replace('http://', '').replace('/', '')

    ssh_username = config.get_cloud_config_value(
        'ssh_username', vm_, __opts__, default='root'
    )
    ssh_password = config.get_cloud_config_value(
        'ssh_password', vm_, __opts__
    )

    ret = {}
    if config.get_cloud_config_value('deploy', vm_, __opts__) is True:
        deploy_script = script(vm_)
        deploy_kwargs = {
            'opts': __opts__,
            'host': hostname,
            'username': ssh_username,
            'password': ssh_password,
            'script': deploy_script,
            'name': vm_['name'],
            'start_action': __opts__['start_action'],
            'parallel': __opts__['parallel'],
            'sock_dir': __opts__['sock_dir'],
            'conf_file': __opts__['conf_file'],
            'minion_pem': vm_['priv_key'],
            'minion_pub': vm_['pub_key'],
            'keep_tmp': __opts__['keep_tmp'],
            'preseed_minion_keys': vm_.get('preseed_minion_keys', None),
            'tmp_dir': config.get_cloud_config_value(
                'tmp_dir', vm_, __opts__, default='/tmp/.saltcloud'
            ),
            'deploy_command': config.get_cloud_config_value(
                'deploy_command', vm_, __opts__,
                default='/tmp/.saltcloud/deploy.sh',
            ),
            'sudo': config.get_cloud_config_value(
                'sudo', vm_, __opts__, default=(ssh_username != 'root')
            ),
            'sudo_password': config.get_cloud_config_value(
                'sudo_password', vm_, __opts__, default=None
            ),
            'tty': config.get_cloud_config_value(
                'tty', vm_, __opts__, default=False
            ),
            'display_ssh_output': config.get_cloud_config_value(
                'display_ssh_output', vm_, __opts__, default=True
            ),
            'script_args': config.get_cloud_config_value(
                'script_args', vm_, __opts__
            ),
            'script_env': config.get_cloud_config_value(
                'script_env', vm_, __opts__
            ),
            'minion_conf': salt.utils.cloud.minion_config(__opts__, vm_)
        }

        # Deploy salt-master files, if necessary
        if config.get_cloud_config_value('make_master', vm_, __opts__) is True:
            deploy_kwargs['make_master'] = True
            deploy_kwargs['master_pub'] = vm_['master_pub']
            deploy_kwargs['master_pem'] = vm_['master_pem']
            master_conf = salt.utils.cloud.master_config(__opts__, vm_)
            deploy_kwargs['master_conf'] = master_conf

            if master_conf.get('syndic_master', None):
                deploy_kwargs['make_syndic'] = True

        deploy_kwargs['make_minion'] = config.get_cloud_config_value(
            'make_minion', vm_, __opts__, default=True
        )

        # Check for Windows install params
        win_installer = config.get_cloud_config_value('win_installer', vm_, __opts__)
        if win_installer:
            deploy_kwargs['win_installer'] = win_installer
            minion = salt.utils.cloud.minion_config(__opts__, vm_)
            deploy_kwargs['master'] = minion['master']
            deploy_kwargs['username'] = config.get_cloud_config_value(
                'win_username', vm_, __opts__, default='Administrator'
            )
            deploy_kwargs['password'] = config.get_cloud_config_value(
                'win_password', vm_, __opts__, default=''
            )

        # Store what was used to the deploy the VM
        event_kwargs = copy.deepcopy(deploy_kwargs)
        del event_kwargs['minion_pem']
        del event_kwargs['minion_pub']
        del event_kwargs['sudo_password']
        if 'password' in event_kwargs:
            del event_kwargs['password']
        ret['deploy_kwargs'] = event_kwargs

        salt.utils.cloud.fire_event(
            'event',
            'executing deploy script',
            'salt/cloud/{0}/deploying'.format(vm_['name']),
            {'kwargs': event_kwargs},
            transport=__opts__['transport']
        )

        deployed = False
        if win_installer:
            deployed = salt.utils.cloud.deploy_windows(**deploy_kwargs)
        else:
            deployed = salt.utils.cloud.deploy_script(**deploy_kwargs)

        if deployed:
            log.info('Salt installed on {0}'.format(vm_['name']))
        else:
            log.error(
                'Failed to start Salt on Cloud VM {0}'.format(
                    vm_['name']
                )
            )

    data = show_instance(vm_['name'], call='action')
    log.info('Created Cloud VM {0[name]!r}'.format(vm_))
    log.debug(
        '{0[name]!r} VM creation details:\n{1}'.format(
            vm_, pprint.pformat(data)
        )
    )

    ret.update(data)

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