    async def stop_notify(self, _uuid: str) -> None:
        """Deactivate notification on a specified characteristic.

        Args:
            _uuid: The characteristic to stop notifying on.

        """
        characteristic = self.characteristics.get(str(_uuid))
        status = await wrap_Task(
            self._bridge.StopNotify(characteristic), loop=self.loop
        )
        if status != GattCommunicationStatus.Success:
            raise BleakError(
                "Could not start notify on {0}: {1}",
                characteristic.Uuid.ToString(),
                status,
            )