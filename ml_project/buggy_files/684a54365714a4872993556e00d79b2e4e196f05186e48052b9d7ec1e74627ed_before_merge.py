    async def connect(self, **kwargs) -> bool:
        """Connect to the specified GATT server.

        Keyword Args:
            timeout (float): Timeout for required ``BleakScanner.find_device_by_address`` call. Defaults to 10.0.

        Returns:
            Boolean representing connection status.

        """
        # Create a new BleakBridge here.
        self._bridge = Bridge()

        # Try to find the desired device.
        if self._device_info is None:
            timeout = kwargs.get("timeout", self._timeout)
            device = await BleakScannerDotNet.find_device_by_address(
                self.address, timeout=timeout
            )

            if device:
                self._device_info = device.details.BluetoothAddress
            else:
                raise BleakError(
                    "Device with address {0} was not found.".format(self.address)
                )

        logger.debug("Connecting to BLE device @ {0}".format(self.address))

        args = [UInt64(self._device_info)]
        if self._address_type is not None:
            args.append(
                BluetoothAddressType.Public
                if self._address_type == "public"
                else BluetoothAddressType.Random
            )
        self._requester = await wrap_IAsyncOperation(
            IAsyncOperation[BluetoothLEDevice](
                BluetoothLEDevice.FromBluetoothAddressAsync(*args)
            ),
            return_type=BluetoothLEDevice,
        )

        loop = asyncio.get_event_loop()

        def _ConnectionStatusChanged_Handler(sender, args):
            logger.debug(
                "_ConnectionStatusChanged_Handler: %d", sender.ConnectionStatus
            )
            if (
                sender.ConnectionStatus == BluetoothConnectionStatus.Disconnected
                and self._disconnected_callback
            ):
                loop.call_soon_threadsafe(self._disconnected_callback, self)

        self._requester.ConnectionStatusChanged += _ConnectionStatusChanged_Handler

        # Obtain services, which also leads to connection being established.
        services = await self.get_services()
        connected = False
        if self._services_resolved:
            # If services has been resolved, then we assume that we are connected. This is due to
            # some issues with getting `is_connected` to give correct response here.
            connected = True
        else:
            for _ in range(5):
                await asyncio.sleep(0.2)
                connected = await self.is_connected()
                if connected:
                    break

        if connected:
            logger.debug("Connection successful.")
        else:
            raise BleakError(
                "Connection to {0} was not successful!".format(self.address)
            )

        return connected