    async def stop_notify(self, _uuid: str) -> None:
        """Deactivate notification/indication on a specified characteristic.

        Args:
            _uuid: The characteristic to stop notifying/indicating on.

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

        self._subscriptions.remove(_uuid)