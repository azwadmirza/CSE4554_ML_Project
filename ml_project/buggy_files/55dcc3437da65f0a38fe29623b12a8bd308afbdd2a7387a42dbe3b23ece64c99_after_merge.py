    async def write_gatt_char(
        self, _uuid: str, data: bytearray, response: bool = False
    ) -> None:
        """Perform a write operation of the specified GATT characteristic.

        Args:
            _uuid (str or UUID): The uuid of the characteristics to write to.
            data (bytes or bytearray): The data to send.
            response (bool): If write-with-response operation should be done. Defaults to `False`.

        """
        characteristic = self.services.get_characteristic(str(_uuid))
        if not characteristic:
            raise BleakError("Characteristic {0} was not found!".format(_uuid))

        writer = DataWriter()
        writer.WriteBytes(Array[Byte](data))
        response = (
            GattWriteOption.WriteWithResponse
            if response
            else GattWriteOption.WriteWithoutResponse
        )
        write_result = await wrap_IAsyncOperation(
            IAsyncOperation[GattWriteResult](
                characteristic.obj.WriteValueWithResultAsync(
                    writer.DetachBuffer(), response
                )
            ),
            return_type=GattWriteResult,
            loop=self.loop,
        )
        if write_result.Status == GattCommunicationStatus.Success:
            logger.debug("Write Characteristic {0} : {1}".format(_uuid, data))
        else:
            raise BleakError(
                "Could not write value {0} to characteristic {1}: {2}".format(
                    data, characteristic.uuid, write_result.Status
                )
            )