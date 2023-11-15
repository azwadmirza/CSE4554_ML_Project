    async def stop_notify(self, _uuid: str) -> None:
        """Stops a notification session from a characteristic.

        Args:
            _uuid (str or uuid.UUID): The UUID of the characteristic to stop
            subscribing to notifications from.

        """
        char_props = self.characteristics.get(_uuid)
        await self._bus.callRemote(
            char_props.get("Path"),
            "StopNotify",
            interface=defs.GATT_CHARACTERISTIC_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="",
            body=[],
            returnSignature="",
        ).asFuture(self.loop)
        self._notification_callbacks.pop(char_props.get("Path"), None)