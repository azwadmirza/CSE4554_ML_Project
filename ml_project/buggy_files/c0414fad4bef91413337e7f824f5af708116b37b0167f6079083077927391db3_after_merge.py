    async def write_gatt_char(
        self, _uuid: str, data: bytearray, response: bool = False
    ) -> None:
        """Perform a write operation on the specified GATT characteristic.

        Args:
            _uuid (str or UUID): The uuid of the characteristics to write to.
            data (bytes or bytearray): The data to send.
            response (bool): If write-with-response operation should be done. Defaults to `False`.

        """
        characteristic = self.services.get_characteristic(str(_uuid))

        if ("write" not in characteristic.properties and "write-without-response" not in characteristic.properties):
            raise BleakError("Characteristic %s does not support write operations!" % str(_uuid))
        if not response and "write-without-response" not in characteristic.properties:
            response = True
            # Force response here, since the device only supports that.
        if response and "write" not in characteristic.properties and "write-without-response" in characteristic.properties:
            response = False
            logger.warning("Characteristic %s does not support Write with response. Trying without..." % str(_uuid))

        if response or (self._bluez_version[0] == 5 and self._bluez_version[1] > 50):
            # TODO: Add OnValueUpdated handler for response=True?
            await self._bus.callRemote(
                characteristic.path,
                "WriteValue",
                interface=defs.GATT_CHARACTERISTIC_INTERFACE,
                destination=defs.BLUEZ_SERVICE,
                signature="aya{sv}",
                body=[data, {"type": "request" if response else "command"}],
                returnSignature="",
            ).asFuture(self.loop)
        else:
            # Older versions of BlueZ don't have the "type" option, so we have
            # to write the hard way. This isn't the most efficient way of doing
            # things, but it works. Also, watch out for txdbus bug that causes
            # returned fd to be None. https://github.com/cocagne/txdbus/pull/81
            fd, _ = await self._bus.callRemote(
                characteristic.path,
                "AcquireWrite",
                interface=defs.GATT_CHARACTERISTIC_INTERFACE,
                destination=defs.BLUEZ_SERVICE,
                signature="a{sv}",
                body=[{}],
                returnSignature="hq",
            ).asFuture(self.loop)
            os.write(fd, data)
            os.close(fd)

        logger.debug(
            "Write Characteristic {0} | {1}: {2}".format(
                _uuid, characteristic.path, data
            )
        )