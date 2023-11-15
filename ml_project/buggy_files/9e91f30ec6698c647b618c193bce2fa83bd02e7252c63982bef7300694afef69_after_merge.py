    async def connect(self, **kwargs) -> bool:
        """Connect to the specified GATT server.

        Keyword Args:
            timeout (float): Timeout for required ``discover`` call. Defaults to 2.0.

        Returns:
            Boolean representing connection status.

        """
        # Try to find the desired device.
        timeout = kwargs.get("timeout", self._timeout)
        devices = await discover(timeout=timeout, loop=self.loop)
        sought_device = list(
            filter(lambda x: x.address.upper() == self.address.upper(), devices)
        )

        if len(sought_device):
            self._device_info = sought_device[0].details
        else:
            raise BleakError(
                "Device with address {0} was " "not found.".format(self.address)
            )

        logger.debug("Connecting to BLE device @ {0}".format(self.address))

        args = [UInt64(self._device_info.BluetoothAddress)]
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
            loop=self.loop,
        )

        def _ConnectionStatusChanged_Handler(sender, args):
            logger.debug("_ConnectionStatusChanged_Handler: " + args.ToString())

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
                await asyncio.sleep(0.2, loop=self.loop)
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