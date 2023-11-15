    async def stop_notify(self, _uuid: str) -> None:
        """Stops a notification session from a characteristic.

        Args:
            _uuid (str or uuid.UUID): The UUID of the characteristic to stop
                subscribing to notifications from.

        """
        characteristic = self.services.get_characteristic(str(_uuid))
        await self._bus.callRemote(
            characteristic.path,
            "StopNotify",
            interface=defs.GATT_CHARACTERISTIC_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="",
            body=[],
            returnSignature="",
        ).asFuture(self.loop)
        self._notification_callbacks.pop(characteristic.path, None)