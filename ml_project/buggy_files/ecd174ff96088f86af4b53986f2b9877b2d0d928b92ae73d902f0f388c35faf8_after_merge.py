    async def get_all_for_characteristic(self, _uuid):
        characteristic = self.services.get_characteristic(str(_uuid))
        out = await self._bus.callRemote(
            characteristic.path,
            "GetAll",
            interface=defs.PROPERTIES_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="s",
            body=[defs.GATT_CHARACTERISTIC_INTERFACE],
            returnSignature="a{sv}",
        ).asFuture(self.loop)
        return out