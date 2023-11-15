    async def stop_notify(self, _uuid: str) -> None:
        """Deactivate notification/indication on a specified characteristic.

        Args:
            _uuid: The characteristic to stop notifying/indicating on.

        """
        characteristic = self.services.get_characteristic(str(_uuid))

        status = await wrap_IAsyncOperation(
            IAsyncOperation[GattCommunicationStatus](
                characteristic.obj.WriteClientCharacteristicConfigurationDescriptorAsync(
                    getattr(
                        GattClientCharacteristicConfigurationDescriptorValue, "None"
                    )
                )
            ),
            return_type=GattCommunicationStatus,
            loop=self.loop,
        )

        if status != GattCommunicationStatus.Success:
            raise BleakError(
                "Could not start notify on {0}: {1}".format(characteristic.uuid, status)
            )
        else:
            callback = self._callbacks.pop(characteristic.uuid)
            self._bridge.RemoveValueChangedCallback(characteristic.obj, callback)