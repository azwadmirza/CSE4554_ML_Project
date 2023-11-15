    async def disconnect(self) -> bool:
        """Disconnect from the specified GATT server.

        Returns:
            Boolean representing if device is disconnected.

        """
        logger.debug("Disconnecting from BLE device...")
        # Remove notifications. Remove them first in the BleakBridge and then clear
        # remaining notifications in Python as well.
        for characteristic in self.services.characteristics.values():
            self._bridge.RemoveValueChangedCallback(characteristic.obj)
        self._notification_callbacks.clear()

        # Dispose all service components that we have requested and created.
        for service in self.services:
            service.obj.Dispose()
        self.services = BleakGATTServiceCollection()
        self._services_resolved = False

        # Dispose of the BluetoothLEDevice and see that the connection
        # status is now Disconnected.
        self._requester.Dispose()
        is_disconnected = (
            self._requester.ConnectionStatus == BluetoothConnectionStatus.Disconnected
        )
        self._requester = None

        # Set device info to None as well.
        self._device_info = None

        # Finally, dispose of the Bleak Bridge as well.
        self._bridge.Dispose()
        self._bridge = None

        return is_disconnected