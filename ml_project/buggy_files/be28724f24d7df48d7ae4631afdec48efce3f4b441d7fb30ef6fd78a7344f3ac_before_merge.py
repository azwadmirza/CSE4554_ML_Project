    async def read_gatt_char(self, _uuid: str) -> bytearray:
        """Read the data on a GATT characteristic.

        Args:
            _uuid (str or uuid.UUID): UUID for the characteristic to read from.

        Returns:
            Byte array of data.

        """
        char_props = self.characteristics.get(str(_uuid))
        if not char_props:
            # TODO: Raise error instead?
            return None

        value = bytearray(
            await self._bus.callRemote(
                char_props.get("Path"),
                "ReadValue",
                interface=defs.GATT_CHARACTERISTIC_INTERFACE,
                destination=defs.BLUEZ_SERVICE,
                signature="a{sv}",
                body=[{}],
                returnSignature="ay",
            ).asFuture(self.loop)
        )

        logger.debug(
            "Read Characteristic {0} | {1}: {2}".format(
                _uuid, char_props.get("Path"), value
            )
        )
        return value