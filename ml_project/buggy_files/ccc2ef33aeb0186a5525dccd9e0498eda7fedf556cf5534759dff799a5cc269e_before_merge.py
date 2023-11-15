    async def _get_device_properties(self):
        return await self._bus.callRemote(
            self._device_path,
            "GetAll",
            interface=defs.PROPERTIES_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="s",
            body=[defs.DEVICE_INTERFACE],
            returnSignature="a{sv}",
        ).asFuture(self.loop)