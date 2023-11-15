def create(vm_):
    '''
    To create a single VM in the VMware environment.

    Sample profile and arguments that can be specified in it can be found
    :ref:`here. <vmware-cloud-profile>`

    CLI Example:

    .. code-block:: bash

        salt-cloud -p vmware-centos6.5 vmname
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

    vm_name = config.get_cloud_config_value(
        'name', vm_, __opts__, default=None
    )
    folder = config.get_cloud_config_value(
        'folder', vm_, __opts__, default=None
    )
    datacenter = config.get_cloud_config_value(
        'datacenter', vm_, __opts__, default=None
    )
    resourcepool = config.get_cloud_config_value(
        'resourcepool', vm_, __opts__, default=None
    )
    cluster = config.get_cloud_config_value(
        'cluster', vm_, __opts__, default=None
    )
    datastore = config.get_cloud_config_value(
        'datastore', vm_, __opts__, default=None
    )
    host = config.get_cloud_config_value(
        'host', vm_, __opts__, default=None
    )
    template = config.get_cloud_config_value(
        'template', vm_, __opts__, default=False
    )
    num_cpus = config.get_cloud_config_value(
        'num_cpus', vm_, __opts__, default=None
    )
    memory = config.get_cloud_config_value(
        'memory', vm_, __opts__, default=None
    )
    devices = config.get_cloud_config_value(
        'devices', vm_, __opts__, default=None
    )
    extra_config = config.get_cloud_config_value(
        'extra_config', vm_, __opts__, default=None
    )
    power = config.get_cloud_config_value(
        'power_on', vm_, __opts__, default=False
    )
    key_filename = config.get_cloud_config_value(
        'private_key', vm_, __opts__, search_global=False, default=None
    )
    deploy = config.get_cloud_config_value(
        'deploy', vm_, __opts__, search_global=False, default=True
    )
    domain = config.get_cloud_config_value(
        'domain', vm_, __opts__, search_global=False, default='local'
    )

    if 'clonefrom' in vm_:
        # Clone VM/template from specified VM/template
        object_ref = _get_mor_by_property(vim.VirtualMachine, vm_['clonefrom'])
        if object_ref.config.template:
            clone_type = "template"
        else:
            clone_type = "vm"

        # Either a cluster, or a resource pool must be specified when cloning from template.
        if resourcepool:
            resourcepool_ref = _get_mor_by_property(vim.ResourcePool, resourcepool)
        elif cluster:
            cluster_ref = _get_mor_by_property(vim.ClusterComputeResource, cluster)
            resourcepool_ref = cluster_ref.resourcePool
        elif clone_type == "template":
            raise SaltCloudSystemExit(
                'You must either specify a cluster, a host or a resource pool'
            )

        # Either a datacenter or a folder can be optionally specified
        # If not specified, the existing VM/template\'s parent folder is used.
        if folder:
            folder_ref = _get_mor_by_property(vim.Folder, folder)
        elif datacenter:
            datacenter_ref = _get_mor_by_property(vim.Datacenter, datacenter)
            folder_ref = datacenter_ref.vmFolder
        else:
            folder_ref = object_ref.parent

        # Create the relocation specs
        reloc_spec = vim.vm.RelocateSpec()

        if resourcepool or cluster:
            reloc_spec.pool = resourcepool_ref

        # Either a datastore/datastore cluster can be optionally specified.
        # If not specified, the current datastore is used.
        if datastore:
            datastore_ref = _get_mor_by_property(vim.Datastore, datastore)

        if host:
            host_ref = _get_mor_by_property(vim.HostSystem, host)
            if host_ref:
                reloc_spec.host = host_ref
            else:
                log.warning("Specified host: {0} does not exist".format(host))
                log.warning("Using host used by the {0} {1}".format(clone_type, vm_['clonefrom']))

        # Create the config specs
        config_spec = vim.vm.ConfigSpec()

        if num_cpus:
            config_spec.numCPUs = num_cpus

        if memory:
            config_spec.memoryMB = memory

        if devices:
            specs = _manage_devices(devices, object_ref)
            config_spec.deviceChange = specs['device_specs']

        if extra_config:
            for key, value in six.iteritems(extra_config):
                option = vim.option.OptionValue(key=key, value=value)
                config_spec.extraConfig.append(option)

        # Create the clone specs
        clone_spec = vim.vm.CloneSpec(
            template=template,
            location=reloc_spec,
            config=config_spec
        )

        if devices and 'network' in devices.keys():
            if "Windows" not in object_ref.config.guestFullName:
                global_ip = vim.vm.customization.GlobalIPSettings()
                if 'dns_servers' in vm_.keys():
                    global_ip.dnsServerList = vm_['dns_servers']

                identity = vim.vm.customization.LinuxPrep()
                hostName = vm_name.split('.')[0]
                domainName = vm_name.split('.', 1)[-1]
                identity.hostName = vim.vm.customization.FixedName(name=hostName)
                identity.domain = domainName if hostName != domainName else domain

                custom_spec = vim.vm.customization.Specification(
                    globalIPSettings=global_ip,
                    identity=identity,
                    nicSettingMap=specs['nics_map']
                )
                clone_spec.customization = custom_spec

        if not template:
            clone_spec.powerOn = power

        log.debug('clone_spec set to {0}\n'.format(
            pprint.pformat(clone_spec))
        )

        try:
            log.info("Creating {0} from {1}({2})\n".format(vm_['name'], clone_type, vm_['clonefrom']))
            salt.utils.cloud.fire_event(
                'event',
                'requesting instance',
                'salt/cloud/{0}/requesting'.format(vm_['name']),
                {'kwargs': vm_},
                transport=__opts__['transport']
            )

            task = object_ref.Clone(folder_ref, vm_name, clone_spec)
            _wait_for_task(task, vm_name, "clone", 5, 'info')
        except Exception as exc:
            log.error(
                'Error creating {0}: {1}'.format(
                    vm_['name'],
                    exc
                ),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            return False

        new_vm_ref = _get_mor_by_property(vim.VirtualMachine, vm_name)

        # If it a template or if it does not need to be powered on, or if deploy is False then do not wait for ip
        if not template and power:
            ip = _wait_for_ip(new_vm_ref, 20)
            if ip:
                log.debug("IP is: {0}".format(ip))
                # ssh or smb using ip and install salt
                if deploy:
                    vm_['key_filename'] = key_filename
                    vm_['ssh_host'] = ip

                    salt.utils.cloud.bootstrap(vm_, __opts__)
            else:
                log.warning("Could not get IP information for {0}".format(vm_name))

        data = show_instance(vm_name, call='action')

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
    else:
        log.error("clonefrom option hasn\'t been specified. Exiting.")
        return False

    return {vm_name: data}