    async def scanForPeripherals_(self, scan_options) -> List[CBPeripheral]:
        """
        Scan for peripheral devices
        scan_options = { service_uuids, timeout }
        """
        # remove old
        self.devices = {}
        service_uuids = []
        if "service_uuids" in scan_options:
            service_uuids_str = scan_options["service_uuids"]
            service_uuids = NSArray.alloc().initWithArray_(
                list(map(string2uuid, service_uuids_str))
            )

        timeout = 0
        if "timeout" in scan_options:
            timeout = float(scan_options["timeout"])

        self.central_manager.scanForPeripheralsWithServices_options_(
            service_uuids, None
        )

        if timeout > 0:
            await asyncio.sleep(timeout)

        self.central_manager.stopScan()
        while self.central_manager.isScanning():
            await asyncio.sleep(0.1)

        return []