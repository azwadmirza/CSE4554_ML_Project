    async def disconnect(self) -> bool:
        """Disconnect from the specified GATT server.

        Returns:
            Boolean representing connection status.

        """
        logger.debug("Disconnecting from BLE device...")
        for rule_name, rule_id in self._rules.items():
            logger.debug("Removing rule {0}, ID: {1}".format(rule_name, rule_id))
            await self._bus.delMatch(rule_id).asFuture(self.loop)
        await self._bus.callRemote(
            self._device_path,
            "Disconnect",
            interface=defs.DEVICE_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
        ).asFuture(self.loop)
        return not await self.is_connected()