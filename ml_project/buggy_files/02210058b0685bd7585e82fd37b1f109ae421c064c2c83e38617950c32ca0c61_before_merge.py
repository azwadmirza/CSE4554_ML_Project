def create(vm_):
    '''
    To create a single VM in the VMware environment.

    Sample profile and arguments that can be specified in it can be found
    :ref:`here. <vmware-cloud-profile>`

    CLI Example:

    .. code-block:: bash

        salt-cloud -p vmware-centos6.5 vmname
    '''
    try:
        # Check for required profile parameters before sending any API calls.
        if vm_['profile'] and config.is_profile_configured(__opts__,
                                        __active_provider_name__ or 'vmware',
                                        vm_['profile'],
                                        vm_=vm_) is False:
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
    cores_per_socket = config.get_cloud_config_value(
        'cores_per_socket', vm_, __opts__, default=None
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
        'power_on', vm_, __opts__, default=True
    )
    key_filename = config.get_cloud_config_value(
        'private_key', vm_, __opts__, search_global=False, default=None
    )
    deploy = config.get_cloud_config_value(
        'deploy', vm_, __opts__, search_global=False, default=True
    )
    wait_for_ip_timeout = config.get_cloud_config_value(
        'wait_for_ip_timeout', vm_, __opts__, default=20 * 60
    )
    domain = config.get_cloud_config_value(
        'domain', vm_, __opts__, search_global=False, default='local'
    )
    hardware_version = config.get_cloud_config_value(
        'hardware_version', vm_, __opts__, search_global=False, default=None
    )
    guest_id = config.get_cloud_config_value(
        'image', vm_, __opts__, search_global=False, default=None
    )
    customization = config.get_cloud_config_value(
        'customization', vm_, __opts__, search_global=False, default=True
    )
    customization_spec = config.get_cloud_config_value(
        'customization_spec', vm_, __opts__, search_global=False, default=None
    )
    win_password = config.get_cloud_config_value(
        'win_password', vm_, __opts__, search_global=False, default=None
    )
    win_organization_name = config.get_cloud_config_value(
        'win_organization_name', vm_, __opts__, search_global=False, default='Organization'
    )
    plain_text = config.get_cloud_config_value(
        'plain_text', vm_, __opts__, search_global=False, default=False
    )
    win_user_fullname = config.get_cloud_config_value(
        'win_user_fullname', vm_, __opts__, search_global=False, default='Windows User'
    )

    # Get service instance object
    si = _get_si()

    container_ref = None

    # If datacenter is specified, set the container reference to start search from it instead
    if datacenter:
        datacenter_ref = salt.utils.vmware.get_mor_by_property(_get_si(), vim.Datacenter, datacenter)
        container_ref = datacenter_ref if datacenter_ref else None

    if 'clonefrom' in vm_:
        # If datacenter is specified, set the container reference to start search from it instead
        if datacenter:
            datacenter_ref = salt.utils.vmware.get_mor_by_property(si, vim.Datacenter, datacenter)
            container_ref = datacenter_ref if datacenter_ref else None

        # Clone VM/template from specified VM/template
        object_ref = salt.utils.vmware.get_mor_by_property(si, vim.VirtualMachine, vm_['clonefrom'], container_ref=container_ref)
        if object_ref:
            clone_type = "template" if object_ref.config.template else "vm"
        else:
            raise SaltCloudSystemExit(
                'The VM/template that you have specified under clonefrom does not exist.'
            )
    else:
        clone_type = None
        object_ref = None

    # Either a cluster, or a resource pool must be specified when cloning from template or creating.
    if resourcepool:
        resourcepool_ref = salt.utils.vmware.get_mor_by_property(si, vim.ResourcePool, resourcepool, container_ref=container_ref)
        if not resourcepool_ref:
            log.error("Specified resource pool: '{0}' does not exist".format(resourcepool))
            if not clone_type or clone_type == "template":
                raise SaltCloudSystemExit('You must specify a resource pool that exists.')
    elif cluster:
        cluster_ref = salt.utils.vmware.get_mor_by_property(si, vim.ClusterComputeResource, cluster, container_ref=container_ref)
        if not cluster_ref:
            log.error("Specified cluster: '{0}' does not exist".format(cluster))
            if not clone_type or clone_type == "template":
                raise SaltCloudSystemExit('You must specify a cluster that exists.')
        else:
            resourcepool_ref = cluster_ref.resourcePool
    elif clone_type == "template":
        raise SaltCloudSystemExit(
            'You must either specify a cluster or a resource pool when cloning from a template.'
        )
    elif not clone_type:
        raise SaltCloudSystemExit(
            'You must either specify a cluster or a resource pool when creating.'
        )
    else:
        log.debug("Using resource pool used by the {0} {1}".format(clone_type, vm_['clonefrom']))

    # Either a datacenter or a folder can be optionally specified when cloning, required when creating.
    # If not specified when cloning, the existing VM/template\'s parent folder is used.
    if folder:
        folder_ref = salt.utils.vmware.get_mor_by_property(si, vim.Folder, folder, container_ref=container_ref)
        if not folder_ref:
            log.error("Specified folder: '{0}' does not exist".format(folder))
            log.debug("Using folder in which {0} {1} is present".format(clone_type, vm_['clonefrom']))
            folder_ref = object_ref.parent
    elif datacenter:
        if not datacenter_ref:
            log.error("Specified datacenter: '{0}' does not exist".format(datacenter))
            log.debug("Using datacenter folder in which {0} {1} is present".format(clone_type, vm_['clonefrom']))
            folder_ref = object_ref.parent
        else:
            folder_ref = datacenter_ref.vmFolder
    elif not clone_type:
        raise SaltCloudSystemExit(
            'You must either specify a folder or a datacenter when creating not cloning.'
        )
    else:
        log.debug("Using folder in which {0} {1} is present".format(clone_type, vm_['clonefrom']))
        folder_ref = object_ref.parent

    if 'clonefrom' in vm_:
        # Create the relocation specs
        reloc_spec = vim.vm.RelocateSpec()

        if (resourcepool and resourcepool_ref) or (cluster and cluster_ref):
            reloc_spec.pool = resourcepool_ref

        # Either a datastore/datastore cluster can be optionally specified.
        # If not specified, the current datastore is used.
        if datastore:
            datastore_ref = salt.utils.vmware.get_mor_by_property(si, vim.Datastore, datastore, container_ref=container_ref)
            if datastore_ref:
                # specific datastore has been specified
                reloc_spec.datastore = datastore_ref
            else:
                datastore_cluster_ref = salt.utils.vmware.get_mor_by_property(si, vim.StoragePod, datastore, container_ref=container_ref)
                if not datastore_cluster_ref:
                    log.error("Specified datastore/datastore cluster: '{0}' does not exist".format(datastore))
                    log.debug("Using datastore used by the {0} {1}".format(clone_type, vm_['clonefrom']))
        else:
            log.debug("No datastore/datastore cluster specified")
            log.debug("Using datastore used by the {0} {1}".format(clone_type, vm_['clonefrom']))

        if host:
            host_ref = salt.utils.vmware.get_mor_by_property(si, vim.HostSystem, host, container_ref=container_ref)
            if host_ref:
                reloc_spec.host = host_ref
            else:
                log.error("Specified host: '{0}' does not exist".format(host))
    else:
        if not datastore:
            raise SaltCloudSystemExit(
                'You must specify a datastore when creating not cloning.'
            )
        else:
            datastore_ref = salt.utils.vmware.get_mor_by_property(si, vim.Datastore, datastore)
            if not datastore_ref:
                raise SaltCloudSystemExit("Specified datastore: '{0}' does not exist".format(datastore))

        if host:
            host_ref = salt.utils.vmware.get_mor_by_property(_get_si(), vim.HostSystem, host, container_ref=container_ref)
            if not host_ref:
                log.error("Specified host: '{0}' does not exist".format(host))

    # Create the config specs
    config_spec = vim.vm.ConfigSpec()

    # If the hardware version is specified and if it is different from the current
    # hardware version, then schedule a hardware version upgrade
    if hardware_version and object_ref is not None:
        hardware_version = "vmx-{0}".format(str(hardware_version).zfill(2))
        if hardware_version != object_ref.config.version:
            log.debug("Scheduling hardware version upgrade from {0} to {1}".format(object_ref.config.version, hardware_version))
            scheduled_hardware_upgrade = vim.vm.ScheduledHardwareUpgradeInfo()
            scheduled_hardware_upgrade.upgradePolicy = 'always'
            scheduled_hardware_upgrade.versionKey = hardware_version
            config_spec.scheduledHardwareUpgradeInfo = scheduled_hardware_upgrade
        else:
            log.debug("Virtual hardware version already set to {0}".format(hardware_version))

    if num_cpus:
        log.debug("Setting cpu to: {0}".format(num_cpus))
        config_spec.numCPUs = int(num_cpus)

    if cores_per_socket:
        log.debug("Setting cores per socket to: {0}".format(cores_per_socket))
        config_spec.numCoresPerSocket = int(cores_per_socket)

    if memory:
        try:
            memory_num, memory_unit = findall(r"[^\W\d_]+|\d+.\d+|\d+", memory)
            if memory_unit.lower() == "mb":
                memory_mb = int(memory_num)
            elif memory_unit.lower() == "gb":
                memory_mb = int(float(memory_num)*1024.0)
            else:
                err_msg = "Invalid memory type specified: '{0}'".format(memory_unit)
                log.error(err_msg)
                return {'Error': err_msg}
        except (TypeError, ValueError):
            memory_mb = int(memory)
        log.debug("Setting memory to: {0} MB".format(memory_mb))
        config_spec.memoryMB = memory_mb

    if devices:
        specs = _manage_devices(devices, vm=object_ref, new_vm_name=vm_name)
        config_spec.deviceChange = specs['device_specs']

    if extra_config:
        for key, value in six.iteritems(extra_config):
            option = vim.option.OptionValue(key=key, value=value)
            config_spec.extraConfig.append(option)

    if 'clonefrom' in vm_:
        clone_spec = handle_snapshot(
            config_spec,
            object_ref,
            reloc_spec,
            template,
            vm_
        )
        if not clone_spec:
            clone_spec = build_clonespec(config_spec,
                                         object_ref,
                                         reloc_spec,
                                         template)

        if customization and customization_spec:
            customization_spec = salt.utils.vmware.get_customizationspec_ref(si=si, customization_spec_name=customization_spec)
            clone_spec.customization = customization_spec.spec
        elif customization and (devices and 'network' in list(devices.keys())):
            global_ip = vim.vm.customization.GlobalIPSettings()
            if 'dns_servers' in list(vm_.keys()):
                global_ip.dnsServerList = vm_['dns_servers']

            non_hostname_chars = compile(r'[^\w-]')
            if search(non_hostname_chars, vm_name):
                hostName = split(non_hostname_chars, vm_name, maxsplit=1)[0]
            else:
                hostName = vm_name
            domainName = hostName.split('.', 1)[-1]

            if 'Windows' not in object_ref.config.guestFullName:
                identity = vim.vm.customization.LinuxPrep()
                identity.hostName = vim.vm.customization.FixedName(name=hostName)
                identity.domain = domainName if hostName != domainName else domain
            else:
                identity = vim.vm.customization.Sysprep()
                identity.guiUnattended = vim.vm.customization.GuiUnattended()
                identity.guiUnattended.autoLogon = True
                identity.guiUnattended.autoLogonCount = 1
                identity.guiUnattended.password = vim.vm.customization.Password()
                identity.guiUnattended.password.value = win_password
                identity.guiUnattended.password.plainText = plain_text
                identity.userData = vim.vm.customization.UserData()
                identity.userData.fullName = win_user_fullname
                identity.userData.orgName = win_organization_name
                identity.userData.computerName = vim.vm.customization.FixedName()
                identity.userData.computerName.name = hostName
                identity.identification = vim.vm.customization.Identification()
            custom_spec = vim.vm.customization.Specification(
                globalIPSettings=global_ip,
                identity=identity,
                nicSettingMap=specs['nics_map']
            )
            clone_spec.customization = custom_spec

        if not template:
            clone_spec.powerOn = power

        log.debug('clone_spec set to:\n{0}'.format(
            pprint.pformat(clone_spec))
        )

    else:
        config_spec.name = vm_name
        config_spec.files = vim.vm.FileInfo()
        config_spec.files.vmPathName = '[{0}] {1}/{1}.vmx'.format(datastore, vm_name)
        config_spec.guestId = guest_id

        log.debug('config_spec set to:\n{0}'.format(
            pprint.pformat(config_spec))
        )

    event_kwargs = vm_.copy()
    del event_kwargs['password']

    try:
        __utils__['cloud.fire_event'](
            'event',
            'requesting instance',
            'salt/cloud/{0}/requesting'.format(vm_['name']),
            args=__utils__['cloud.filter_event']('requesting', event_kwargs, event_kwargs.keys()),
            sock_dir=__opts__['sock_dir'],
            transport=__opts__['transport']
        )

        if 'clonefrom' in vm_:
            log.info("Creating {0} from {1}({2})".format(vm_['name'], clone_type, vm_['clonefrom']))

            if datastore and not datastore_ref and datastore_cluster_ref:
                # datastore cluster has been specified so apply Storage DRS recomendations
                pod_spec = vim.storageDrs.PodSelectionSpec(storagePod=datastore_cluster_ref)

                storage_spec = vim.storageDrs.StoragePlacementSpec(
                    type='clone',
                    vm=object_ref,
                    podSelectionSpec=pod_spec,
                    cloneSpec=clone_spec,
                    cloneName=vm_name,
                    folder=folder_ref
                )

                # get recommended datastores
                recommended_datastores = si.content.storageResourceManager.RecommendDatastores(storageSpec=storage_spec)

                # apply storage DRS recommendations
                task = si.content.storageResourceManager.ApplyStorageDrsRecommendation_Task(recommended_datastores.recommendations[0].key)
                salt.utils.vmware.wait_for_task(task, vm_name, 'apply storage DRS recommendations', 5, 'info')
            else:
                # clone the VM/template
                task = object_ref.Clone(folder_ref, vm_name, clone_spec)
                salt.utils.vmware.wait_for_task(task, vm_name, 'clone', 5, 'info')
        else:
            log.info('Creating {0}'.format(vm_['name']))

            if host:
                task = folder_ref.CreateVM_Task(config_spec, resourcepool_ref, host_ref)
            else:
                task = folder_ref.CreateVM_Task(config_spec, resourcepool_ref)
            salt.utils.vmware.wait_for_task(task, vm_name, "create", 15, 'info')
    except Exception as exc:
        err_msg = 'Error creating {0}: {1}'.format(vm_['name'], exc)
        log.error(
            err_msg,
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return {'Error': err_msg}

    new_vm_ref = salt.utils.vmware.get_mor_by_property(si, vim.VirtualMachine, vm_name, container_ref=container_ref)

    # Find how to power on in CreateVM_Task (if possible), for now this will do
    try:
        if not clone_type and power:
            task = new_vm_ref.PowerOn()
            salt.utils.vmware.wait_for_task(task, vm_name, 'power', 5, 'info')
    except Exception as exc:
        log.info('Powering on the VM threw this exception. Ignoring.')
        log.info(exc)

    # If it a template or if it does not need to be powered on then do not wait for the IP
    out = None
    if not template and power:
        ip = _wait_for_ip(new_vm_ref, wait_for_ip_timeout)
        if ip:
            log.info("[ {0} ] IPv4 is: {1}".format(vm_name, ip))
            # ssh or smb using ip and install salt only if deploy is True
            if deploy:
                vm_['key_filename'] = key_filename
                vm_['ssh_host'] = ip

                out = __utils__['cloud.bootstrap'](vm_, __opts__)

    data = show_instance(vm_name, call='action')

    if deploy and out is not None:
        data['deploy_kwargs'] = out['deploy_kwargs']

    __utils__['cloud.fire_event'](
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(vm_['name']),
        args=__utils__['cloud.filter_event']('created', vm_, ['name', 'profile', 'provider', 'driver']),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )
    return data