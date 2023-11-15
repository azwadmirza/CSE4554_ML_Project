    async def disconnect(self) -> bool:
        """Disconnect from the specified GATT server.

        Returns:
            Boolean representing connection status.

        """
        logger.debug("Disconnecting from BLE device...")

        await self._cleanup()

        await self._bus.callRemote(
            self._device_path,
            "Disconnect",
            interface=defs.DEVICE_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
        ).asFuture(self.loop)
        return not await self.is_connected()