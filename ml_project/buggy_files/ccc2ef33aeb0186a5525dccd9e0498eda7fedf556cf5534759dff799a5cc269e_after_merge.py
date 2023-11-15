    async def _get_device_properties(self, interface=defs.DEVICE_INTERFACE):
        return await self._bus.callRemote(
            self._device_path,
            "GetAll",
            interface=defs.PROPERTIES_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="s",
            body=[interface],
            returnSignature="a{sv}",
        ).asFuture(self.loop)