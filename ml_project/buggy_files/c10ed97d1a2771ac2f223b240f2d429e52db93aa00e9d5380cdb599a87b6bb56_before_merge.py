    async def read_gatt_char(self, _uuid: str) -> bytearray:
        """Perform read operation on the specified characteristic.

        Args:
            _uuid (str or UUID): The uuid of the characteristics to start notification on.

        Returns:
            (bytearray) The read data.

        """
        characteristic = self.characteristics.get(str(_uuid))
        if not characteristic:
            raise BleakError("Characteristic {0} was not found!".format(_uuid))

        read_results = await wrap_Task(
            self._bridge.ReadCharacteristicValueAsync(characteristic), loop=self.loop
        )
        status, value = read_results.Item1, bytearray(read_results.Item2)
        if status == GattCommunicationStatus.Success:
            logger.debug("Read Characteristic {0} : {1}".format(_uuid, value))
        else:
            raise BleakError(
                "Could not read characteristic value for {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )

        return value