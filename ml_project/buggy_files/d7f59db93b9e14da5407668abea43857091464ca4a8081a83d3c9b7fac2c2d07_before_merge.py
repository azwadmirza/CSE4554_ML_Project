def request_instance(vm_):
    """
    Request a VM from Azure.
    """
    compconn = get_conn(client_type="compute")

    # pylint: disable=invalid-name
    CachingTypes = getattr(compute_models, "CachingTypes")
    # pylint: disable=invalid-name
    DataDisk = getattr(compute_models, "DataDisk")
    # pylint: disable=invalid-name
    DiskCreateOptionTypes = getattr(compute_models, "DiskCreateOptionTypes")
    # pylint: disable=invalid-name
    HardwareProfile = getattr(compute_models, "HardwareProfile")
    # pylint: disable=invalid-name
    ImageReference = getattr(compute_models, "ImageReference")
    # pylint: disable=invalid-name
    LinuxConfiguration = getattr(compute_models, "LinuxConfiguration")
    # pylint: disable=invalid-name
    SshConfiguration = getattr(compute_models, "SshConfiguration")
    # pylint: disable=invalid-name
    SshPublicKey = getattr(compute_models, "SshPublicKey")
    # pylint: disable=invalid-name
    NetworkInterfaceReference = getattr(compute_models, "NetworkInterfaceReference")
    # pylint: disable=invalid-name
    NetworkProfile = getattr(compute_models, "NetworkProfile")
    # pylint: disable=invalid-name
    OSDisk = getattr(compute_models, "OSDisk")
    # pylint: disable=invalid-name
    OSProfile = getattr(compute_models, "OSProfile")
    # pylint: disable=invalid-name
    StorageProfile = getattr(compute_models, "StorageProfile")
    # pylint: disable=invalid-name
    VirtualHardDisk = getattr(compute_models, "VirtualHardDisk")
    # pylint: disable=invalid-name
    VirtualMachine = getattr(compute_models, "VirtualMachine")
    # pylint: disable=invalid-name
    VirtualMachineSizeTypes = getattr(compute_models, "VirtualMachineSizeTypes")

    subscription_id = config.get_cloud_config_value(
        "subscription_id", get_configured_provider(), __opts__, search_global=False
    )

    if vm_.get("driver") is None:
        vm_["driver"] = "azurearm"

    if vm_.get("location") is None:
        vm_["location"] = get_location()

    if vm_.get("resource_group") is None:
        vm_["resource_group"] = config.get_cloud_config_value(
            "resource_group", vm_, __opts__, search_global=True
        )

    if vm_.get("name") is None:
        vm_["name"] = config.get_cloud_config_value(
            "name", vm_, __opts__, search_global=True
        )

    # pylint: disable=unused-variable
    iface_data, public_ips, private_ips = create_network_interface(
        call="action", kwargs=vm_
    )
    vm_["iface_id"] = iface_data["id"]

    disk_name = "{0}-vol0".format(vm_["name"])

    vm_username = config.get_cloud_config_value(
        "ssh_username",
        vm_,
        __opts__,
        search_global=True,
        default=config.get_cloud_config_value(
            "win_username", vm_, __opts__, search_global=True
        ),
    )

    ssh_publickeyfile_contents = None
    ssh_publickeyfile = config.get_cloud_config_value(
        "ssh_publickeyfile", vm_, __opts__, search_global=False, default=None
    )
    if ssh_publickeyfile is not None:
        try:
            with salt.utils.files.fopen(ssh_publickeyfile, "r") as spkc_:
                ssh_publickeyfile_contents = spkc_.read()
        except Exception as exc:  # pylint: disable=broad-except
            raise SaltCloudConfigError(
                "Failed to read ssh publickey file '{0}': "
                "{1}".format(ssh_publickeyfile, exc.args[-1])
            )

    disable_password_authentication = config.get_cloud_config_value(
        "disable_password_authentication",
        vm_,
        __opts__,
        search_global=False,
        default=False,
    )

    os_kwargs = {}
    win_installer = config.get_cloud_config_value(
        "win_installer", vm_, __opts__, search_global=True
    )
    if not win_installer and ssh_publickeyfile_contents is not None:
        sshpublickey = SshPublicKey(
            key_data=ssh_publickeyfile_contents,
            path="/home/{0}/.ssh/authorized_keys".format(vm_username),
        )
        sshconfiguration = SshConfiguration(public_keys=[sshpublickey],)
        linuxconfiguration = LinuxConfiguration(
            disable_password_authentication=disable_password_authentication,
            ssh=sshconfiguration,
        )
        os_kwargs["linux_configuration"] = linuxconfiguration
        vm_password = None
    else:
        vm_password = salt.utils.stringutils.to_str(
            config.get_cloud_config_value(
                "ssh_password",
                vm_,
                __opts__,
                search_global=True,
                default=config.get_cloud_config_value(
                    "win_password", vm_, __opts__, search_global=True
                ),
            )
        )

    if win_installer or (
        vm_password is not None and not disable_password_authentication
    ):
        if not isinstance(vm_password, str):
            raise SaltCloudSystemExit("The admin password must be a string.")
        if len(vm_password) < 8 or len(vm_password) > 123:
            raise SaltCloudSystemExit(
                "The admin password must be between 8-123 characters long."
            )
        complexity = 0
        if any(char.isdigit() for char in vm_password):
            complexity += 1
        if any(char.isupper() for char in vm_password):
            complexity += 1
        if any(char.islower() for char in vm_password):
            complexity += 1
        if any(char in string.punctuation for char in vm_password):
            complexity += 1
        if complexity < 3:
            raise SaltCloudSystemExit(
                "The admin password must contain at least 3 of the following types: "
                "upper, lower, digits, special characters"
            )
        os_kwargs["admin_password"] = vm_password

    availability_set = config.get_cloud_config_value(
        "availability_set", vm_, __opts__, search_global=False, default=None
    )
    if availability_set is not None and isinstance(availability_set, six.string_types):
        availability_set = {
            "id": "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Compute/availabilitySets/{2}".format(
                subscription_id, vm_["resource_group"], availability_set
            )
        }
    else:
        availability_set = None

    cloud_env = _get_cloud_environment()

    storage_endpoint_suffix = cloud_env.suffixes.storage_endpoint

    if isinstance(vm_.get("volumes"), six.string_types):
        volumes = salt.utils.yaml.safe_load(vm_["volumes"])
    else:
        volumes = vm_.get("volumes")

    data_disks = None
    if isinstance(volumes, list):
        data_disks = []
    else:
        volumes = []

    lun = 0
    luns = []
    for volume in volumes:
        if isinstance(volume, six.string_types):
            volume = {"name": volume}

        volume.setdefault(
            "name",
            volume.get(
                "name",
                volume.get(
                    "name", "{0}-datadisk{1}".format(vm_["name"], six.text_type(lun))
                ),
            ),
        )

        volume.setdefault(
            "disk_size_gb",
            volume.get("logical_disk_size_in_gb", volume.get("size", 100)),
        )
        # Old kwarg was host_caching, new name is caching
        volume.setdefault("caching", volume.get("host_caching", "ReadOnly"))
        while lun in luns:
            lun += 1
            if lun > 15:
                log.error("Maximum lun count has been reached")
                break
        volume.setdefault("lun", lun)
        lun += 1
        # The default vhd is {vm_name}-datadisk{lun}.vhd
        if "media_link" in volume:
            volume["vhd"] = VirtualHardDisk(volume["media_link"])
            del volume["media_link"]
        elif volume.get("vhd") == "unmanaged":
            volume["vhd"] = VirtualHardDisk(
                "https://{0}.blob.{1}/vhds/{2}-datadisk{3}.vhd".format(
                    vm_["storage_account"],
                    storage_endpoint_suffix,
                    vm_["name"],
                    volume["lun"],
                ),
            )
        elif "vhd" in volume:
            volume["vhd"] = VirtualHardDisk(volume["vhd"])

        if "image" in volume:
            volume["create_option"] = "from_image"
        elif "attach" in volume:
            volume["create_option"] = "attach"
        else:
            volume["create_option"] = "empty"
        data_disks.append(DataDisk(**volume))

    img_ref = None
    if vm_["image"].startswith("http") or vm_.get("vhd") == "unmanaged":
        if vm_["image"].startswith("http"):
            source_image = VirtualHardDisk(vm_["image"])
        else:
            source_image = None
            if "|" in vm_["image"]:
                img_pub, img_off, img_sku, img_ver = vm_["image"].split("|")
                img_ref = ImageReference(
                    publisher=img_pub, offer=img_off, sku=img_sku, version=img_ver,
                )
            elif vm_["image"].startswith("/subscriptions"):
                img_ref = ImageReference(id=vm_["image"])
        if win_installer:
            os_type = "Windows"
        else:
            os_type = "Linux"
        os_disk = OSDisk(
            caching=CachingTypes.none,
            create_option=DiskCreateOptionTypes.from_image,
            name=disk_name,
            vhd=VirtualHardDisk(
                "https://{0}.blob.{1}/vhds/{2}.vhd".format(
                    vm_["storage_account"], storage_endpoint_suffix, disk_name,
                ),
            ),
            os_type=os_type,
            image=source_image,
            disk_size_gb=vm_.get("os_disk_size_gb"),
        )
    else:
        source_image = None
        os_type = None
        os_disk = OSDisk(
            create_option=DiskCreateOptionTypes.from_image,
            disk_size_gb=vm_.get("os_disk_size_gb"),
        )
        if "|" in vm_["image"]:
            img_pub, img_off, img_sku, img_ver = vm_["image"].split("|")
            img_ref = ImageReference(
                publisher=img_pub, offer=img_off, sku=img_sku, version=img_ver,
            )
        elif vm_["image"].startswith("/subscriptions"):
            img_ref = ImageReference(id=vm_["image"])

    userdata_file = config.get_cloud_config_value(
        "userdata_file", vm_, __opts__, search_global=False, default=None
    )
    userdata = config.get_cloud_config_value(
        "userdata", vm_, __opts__, search_global=False, default=None
    )
    userdata_template = config.get_cloud_config_value(
        "userdata_template", vm_, __opts__, search_global=False, default=None
    )

    if userdata_file:
        if os.path.exists(userdata_file):
            with salt.utils.files.fopen(userdata_file, "r") as fh_:
                userdata = fh_.read()

    if userdata and userdata_template:
        userdata_sendkeys = config.get_cloud_config_value(
            "userdata_sendkeys", vm_, __opts__, search_global=False, default=None
        )
        if userdata_sendkeys:
            vm_["priv_key"], vm_["pub_key"] = salt.utils.cloud.gen_keys(
                config.get_cloud_config_value("keysize", vm_, __opts__)
            )

            key_id = vm_.get("name")
            if "append_domain" in vm_:
                key_id = ".".join([key_id, vm_["append_domain"]])

            salt.utils.cloud.accept_key(__opts__["pki_dir"], vm_["pub_key"], key_id)

        userdata = salt.utils.cloud.userdata_template(__opts__, vm_, userdata)

    custom_extension = None
    if userdata is not None or userdata_file is not None:
        try:
            if win_installer:
                publisher = "Microsoft.Compute"
                virtual_machine_extension_type = "CustomScriptExtension"
                type_handler_version = "1.8"
                if userdata_file and userdata_file.endswith(".ps1"):
                    command_prefix = "powershell -ExecutionPolicy Unrestricted -File "
                else:
                    command_prefix = ""
            else:
                publisher = "Microsoft.Azure.Extensions"
                virtual_machine_extension_type = "CustomScript"
                type_handler_version = "2.0"
                command_prefix = ""

            settings = {}
            if userdata:
                settings["commandToExecute"] = userdata
            elif userdata_file.startswith("http"):
                settings["fileUris"] = [userdata_file]
                settings["commandToExecute"] = (
                    command_prefix
                    + "./"
                    + userdata_file[userdata_file.rfind("/") + 1 :]
                )

            custom_extension = {
                "resource_group": vm_["resource_group"],
                "virtual_machine_name": vm_["name"],
                "extension_name": vm_["name"] + "_custom_userdata_script",
                "location": vm_["location"],
                "publisher": publisher,
                "virtual_machine_extension_type": virtual_machine_extension_type,
                "type_handler_version": type_handler_version,
                "auto_upgrade_minor_version": True,
                "settings": settings,
                "protected_settings": None,
            }
        except Exception as exc:  # pylint: disable=broad-except
            log.exception("Failed to encode userdata: %s", exc)

    params = VirtualMachine(
        location=vm_["location"],
        plan=None,
        hardware_profile=HardwareProfile(
            vm_size=getattr(VirtualMachineSizeTypes, vm_["size"].lower()),
        ),
        storage_profile=StorageProfile(
            os_disk=os_disk, data_disks=data_disks, image_reference=img_ref,
        ),
        os_profile=OSProfile(
            admin_username=vm_username, computer_name=vm_["name"], **os_kwargs
        ),
        network_profile=NetworkProfile(
            network_interfaces=[NetworkInterfaceReference(id=vm_["iface_id"])],
        ),
        availability_set=availability_set,
    )

    __utils__["cloud.fire_event"](
        "event",
        "requesting instance",
        "salt/cloud/{0}/requesting".format(vm_["name"]),
        args=__utils__["cloud.filter_event"](
            "requesting", vm_, ["name", "profile", "provider", "driver"]
        ),
        sock_dir=__opts__["sock_dir"],
        transport=__opts__["transport"],
    )

    try:
        vm_create = compconn.virtual_machines.create_or_update(
            resource_group_name=vm_["resource_group"],
            vm_name=vm_["name"],
            parameters=params,
        )
        vm_create.wait()
        vm_result = vm_create.result()
        vm_result = vm_result.as_dict()
        if custom_extension:
            create_or_update_vmextension(kwargs=custom_extension)
    except CloudError as exc:
        __utils__["azurearm.log_cloud_error"]("compute", exc.message)
        vm_result = {}

    return vm_result