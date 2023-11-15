    async def write_gatt_char(
        self, _uuid: str, data: bytearray, response: bool = False
    ) -> Any:
        """Write data to a GATT characteristic.

        Args:
            _uuid (str or uuid.UUID): The UUID of the GATT characteristic to write to.
            data (bytearray): The data to write.
            response (bool): If write with response should be done.

        Returns:
            None if not `response=True`, in which case a bytearray is returned.

        """
        characteristic = self.services.get_characteristic(str(_uuid))
        await self._bus.callRemote(
            characteristic.path,
            "WriteValue",
            interface=defs.GATT_CHARACTERISTIC_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="aya{sv}",
            body=[data, {}],
            returnSignature="",
        ).asFuture(self.loop)
        logger.debug(
            "Write Characteristic {0} | {1}: {2}".format(
                _uuid, characteristic.path, data
            )
        )
        if response:
            return await self.read_gatt_char(_uuid)