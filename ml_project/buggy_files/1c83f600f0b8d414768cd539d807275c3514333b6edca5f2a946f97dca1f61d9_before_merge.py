async def discover(
    timeout: float = 5.0, loop: AbstractEventLoop = None, **kwargs
) -> List[BLEDevice]:
    """Perform a Bluetooth LE Scan using Windows.Devices.Bluetooth.Advertisement

    Args:
        timeout (float): Time to scan for.
        loop (Event Loop): The event loop to use.

    Keyword Args:
        string_output (bool): If set to false, ``discover`` returns .NET
            device objects instead.

    Returns:
        List of strings or objects found.

    """
    loop = loop if loop else asyncio.get_event_loop()

    watcher = BluetoothLEAdvertisementWatcher()

    devices = {}
    scan_responses = {}

    def _format_bdaddr(a):
        return ":".join("{:02X}".format(x) for x in a.to_bytes(6, byteorder="big"))

    def _format_event_args(e):
        try:
            return "{0}: {1}".format(
                _format_bdaddr(e.BluetoothAddress),
                e.Advertisement.LocalName or "Unknown",
            )
        except Exception:
            return e.BluetoothAddress

    def AdvertisementWatcher_Received(sender, e):
        if sender == watcher:
            logger.debug("Received {0}.".format(_format_event_args(e)))
            if e.AdvertisementType == BluetoothLEAdvertisementType.ScanResponse:
                if e.BluetoothAddress not in scan_responses:
                    scan_responses[e.BluetoothAddress] = e
            else:
                if e.BluetoothAddress not in devices:
                    devices[e.BluetoothAddress] = e

    def AdvertisementWatcher_Stopped(sender, e):
        if sender == watcher:
            logger.debug(
                "{0} devices found. Watcher status: {1}.".format(
                    len(devices), watcher.Status
                )
            )

    watcher.Received += AdvertisementWatcher_Received
    watcher.Stopped += AdvertisementWatcher_Stopped

    watcher.ScanningMode = BluetoothLEScanningMode.Active

    # Watcher works outside of the Python process.
    watcher.Start()
    await asyncio.sleep(timeout, loop=loop)
    watcher.Stop()

    try:
        watcher.Received -= AdvertisementWatcher_Received
        watcher.Stopped -= AdvertisementWatcher_Stopped
    except Exception as e:
        logger.debug("Could not remove event handlers: {0}...".format(e))

    found = []
    for d in devices.values():
        bdaddr = _format_bdaddr(d.BluetoothAddress)
        uuids = []
        for u in d.Advertisement.ServiceUuids:
            uuids.append(u.ToString())
        data = {}
        for m in d.Advertisement.ManufacturerData:
            md = IBuffer(m.Data)
            b = Array.CreateInstance(Byte, md.Length)
            reader = DataReader.FromBuffer(md)
            reader.ReadBytes(b)
            data[m.CompanyId] = bytes(b)
        local_name = d.Advertisement.LocalName
        if not local_name and d.BluetoothAddress in scan_responses:
            local_name = scan_responses[d.BluetoothAddress].Advertisement.LocalName
        found.append(
            BLEDevice(
                bdaddr,
                local_name,
                d,
                uuids=uuids,
                manufacturer_data=data,
            )
        )

    return found