    async def connect(self) -> bool:
        """Connect to the specified GATT server.

        Returns:
            Boolean representing connection status.

        """

        # Create system bus
        self._bus = await txdbus_connect(reactor, busAddress="system").asFuture(
            self.loop
        )
        # TODO: Handle path errors from txdbus/dbus
        self._device_path = get_device_object_path(self.device, self.address)

        def _services_resolved_callback(message):
            iface, changed, invalidated = message.body
            is_resolved = defs.DEVICE_INTERFACE and changed.get(
                "ServicesResolved", False
            )
            if iface == is_resolved:
                logger.info("Services resolved.")
                self.services_resolved = True

        rule_id = await signals.listen_properties_changed(
            self._bus, self.loop, _services_resolved_callback
        )

        logger.debug(
            "Connecting to BLE device @ {0} with {1}".format(self.address, self.device)
        )
        try:
            await self._bus.callRemote(
                self._device_path,
                "Connect",
                interface="org.bluez.Device1",
                destination="org.bluez",
            ).asFuture(self.loop)
        except RemoteError as e:
            raise BleakError(str(e))

        if await self.is_connected():
            logger.debug("Connection successful.")
        else:
            raise BleakError(
                "Connection to {0} was not successful!".format(self.address)
            )

        # Get all services. This means making the actual connection.
        await self.get_services()
        properties = await self._get_device_properties()
        if not properties.get("Connected"):
            raise BleakError("Connection failed!")

        await self._bus.delMatch(rule_id).asFuture(self.loop)
        self._rules["PropChanged"] = await signals.listen_properties_changed(
            self._bus, self.loop, self._properties_changed_callback
        )
        return True