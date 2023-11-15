    async def read_gatt_char(self, _uuid: str) -> bytearray:
        """Read the data on a GATT characteristic.

        Args:
            _uuid (str or uuid.UUID): UUID for the characteristic to read from.

        Returns:
            Byte array of data.

        """
        characteristic = self.services.get_characteristic(str(_uuid))
        if not characteristic:
            # Special handling for BlueZ >= 5.48, where Battery Service (0000180f-0000-1000-8000-00805f9b34fb:)
            # has been moved to interface org.bluez.Battery1 instead of as a regular service.
            if _uuid == "00002a19-0000-1000-8000-00805f9b34fb" and (
                self._bluez_version[0] == 5 and self._bluez_version[1] >= 48
            ):
                props = await self._get_device_properties(
                    interface=defs.BATTERY_INTERFACE
                )
                # Simulate regular characteristics read to be consistent over all platforms.
                value = bytearray([props.get("Percentage", "")])
                logger.debug(
                    "Read Battery Level {0} | {1}: {2}".format(
                        _uuid, self._device_path, value
                    )
                )
                return value
            raise BleakError(
                "Characteristic with UUID {0} could not be found!".format(_uuid)
            )

        value = bytearray(
            await self._bus.callRemote(
                characteristic.path,
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
                _uuid, characteristic.path, value
            )
        )
        return value