    async def is_connected(self) -> bool:
        """Check connection status between this client and the server.

        Returns:
            Boolean representing connection status.

        """
        # TODO: Listen to connected property changes.
        return await self._bus.callRemote(
            self._device_path,
            "Get",
            interface=defs.PROPERTIES_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="ss",
            body=[defs.DEVICE_INTERFACE, "Connected"],
            returnSignature="v",
        ).asFuture(asyncio.get_event_loop())