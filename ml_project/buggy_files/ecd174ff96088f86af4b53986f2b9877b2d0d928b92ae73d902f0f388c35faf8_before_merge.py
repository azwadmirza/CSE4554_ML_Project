    async def get_all_for_characteristic(self, _uuid):
        char_props = self.characteristics.get(str(_uuid))
        out = await self._bus.callRemote(
            char_props.get("Path"),
            "GetAll",
            interface=defs.PROPERTIES_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="s",
            body=[defs.GATT_CHARACTERISTIC_INTERFACE],
            returnSignature="a{sv}",
        ).asFuture(self.loop)
        return out