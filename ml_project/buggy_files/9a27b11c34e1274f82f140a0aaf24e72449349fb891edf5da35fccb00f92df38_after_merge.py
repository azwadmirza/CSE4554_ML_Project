async def discover(timeout=5.0, loop=None, **kwargs):
    """Discover nearby Bluetooth Low Energy devices.

    Args:
        timeout (float): Duration to scan for.
        loop (asyncio.AbstractEventLoop): Optional event loop to use.

    Keyword Args:
        device (str): Bluetooth device to use for discovery.

    Returns:
        List of tuples containing name, address and signal strength
        of nearby devices.

    """
    device = kwargs.get("device", "hci0")
    loop = loop if loop else asyncio.get_event_loop()
    cached_devices = {}
    devices = {}
    rules = list()

    def parse_msg(message):
        if message.member == "InterfacesAdded":
            msg_path = message.body[0]
            try:
                device_interface = message.body[1].get("org.bluez.Device1", {})
            except Exception as e:
                raise e
            devices[msg_path] = (
                {**devices[msg_path], **device_interface}
                if msg_path in devices
                else device_interface
            )
        elif message.member == "PropertiesChanged":
            iface, changed, invalidated = message.body
            if iface != defs.DEVICE_INTERFACE:
                return

            msg_path = message.path
            # the PropertiesChanged signal only sends changed properties, so we
            # need to get remaining properties from cached_devices. However, we
            # don't want to add all cached_devices to the devices dict since
            # they may not actually be nearby or powered on.
            if msg_path not in devices and msg_path in cached_devices:
                devices[msg_path] = cached_devices[msg_path]
            devices[msg_path] = (
                {**devices[msg_path], **changed} if msg_path in devices else changed
            )
        elif (
            message.member == "InterfacesRemoved"
            and message.body[1][0] == defs.BATTERY_INTERFACE
        ):
            logger.info(
                "{0}, {1} ({2}): {3}".format(
                    message.member, message.interface, message.path, message.body
                )
            )
            return
        else:
            msg_path = message.path
            logger.info(
                "{0}, {1} ({2}): {3}".format(
                    message.member, message.interface, message.path, message.body
                )
            )

        logger.info(
            "{0}, {1} ({2} dBm), Object Path: {3}".format(
                *_device_info(msg_path, devices.get(msg_path))
            )
        )

    bus = await client.connect(reactor, "system").asFuture(loop)

    # Add signal listeners
    rules.append(
        await bus.addMatch(
            parse_msg,
            interface="org.freedesktop.DBus.ObjectManager",
            member="InterfacesAdded",
        ).asFuture(loop)
    )
    rules.append(
        await bus.addMatch(
            parse_msg,
            interface="org.freedesktop.DBus.ObjectManager",
            member="InterfacesRemoved",
        ).asFuture(loop)
    )
    rules.append(
        await bus.addMatch(
            parse_msg,
            interface="org.freedesktop.DBus.Properties",
            member="PropertiesChanged",
        ).asFuture(loop)
    )

    # Find the HCI device to use for scanning and get cached device properties
    objects = await bus.callRemote(
        "/",
        "GetManagedObjects",
        interface=defs.OBJECT_MANAGER_INTERFACE,
        destination=defs.BLUEZ_SERVICE,
    ).asFuture(loop)
    adapter_path, interface = _filter_on_adapter(objects, device)
    cached_devices = dict(_filter_on_device(objects))

    # dd = {'objectPath': '/org/bluez/hci0', 'methodName': 'StartDiscovery',
    # 'interface': 'org.bluez.Adapter1', 'destination': 'org.bluez',
    # 'signature': '', 'body': (), 'expectReply': True, 'autoStart': True,
    # 'timeout': None, 'returnSignature': ''}
    # Running Discovery loop.
    await bus.callRemote(
        adapter_path,
        "SetDiscoveryFilter",
        interface="org.bluez.Adapter1",
        destination="org.bluez",
        signature="a{sv}",
        body=[{"Transport": "le"}],
    ).asFuture(loop)
    await bus.callRemote(
        adapter_path,
        "StartDiscovery",
        interface="org.bluez.Adapter1",
        destination="org.bluez",
    ).asFuture(loop)
    await asyncio.sleep(timeout)
    await bus.callRemote(
        adapter_path,
        "StopDiscovery",
        interface="org.bluez.Adapter1",
        destination="org.bluez",
    ).asFuture(loop)

    # Reduce output.
    # out = []
    # for path, props in devices.items():
    #    properties = await cli.callRemote(
    #        path, 'GetAll',
    #        interface=defs.PROPERTIES_INTERFACE,
    #        destination=defs.BLUEZ_SERVICE,
    #        signature='s',
    #        body=[defs.DEVICE_INTERFACE, ],
    #        returnSignature='a{sv}').asFuture(loop)
    #    print(properties)
    #
    discovered_devices = []
    for path, props in devices.items():
        if not props:
            logger.debug(
                "Disregarding %s since no properties could be obtained." % path
            )
            continue
        name, address, _, path = _device_info(path, props)
        if address is None:
            continue
        uuids = props.get("UUIDs", [])
        manufacturer_data = props.get("ManufacturerData", {})
        discovered_devices.append(
            BLEDevice(
                address,
                name,
                {"path": path, "props": props},
                uuids=uuids,
                manufacturer_data=manufacturer_data,
            )
        )

    for rule in rules:
        await bus.delMatch(rule).asFuture(loop)

    bus.disconnect()

    return discovered_devices