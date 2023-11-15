    async def write_gatt_char(
        self, _uuid: str, data: bytearray, response: bool = False
    ) -> Any:
        """Write data to a GATT characteristic.

        Args:
            _uuid (str or uuid.UUID): The UUID of the GATT
            characteristic to write to.
            data (bytearray):
            response (bool): Write with response.

        Returns:
            None if not `response=True`, in which case a bytearray is returned.

        """
        char_props = self.characteristics.get(str(_uuid))
        await self._bus.callRemote(
            char_props.get("Path"),
            "WriteValue",
            interface=defs.GATT_CHARACTERISTIC_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="aya{sv}",
            body=[data, {}],
            returnSignature="",
        ).asFuture(self.loop)
        logger.debug(
            "Write Characteristic {0} | {1}: {2}".format(
                _uuid, char_props.get("Path"), data
            )
        )
        if response:
            return await self.read_gatt_char(_uuid)