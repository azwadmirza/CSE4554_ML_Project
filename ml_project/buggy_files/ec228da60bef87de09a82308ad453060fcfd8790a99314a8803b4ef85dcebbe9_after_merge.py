    async def disconnect(self) -> bool:
        """Disconnect from the specified GATT server.

        Returns:
            Boolean representing if device is disconnected.

        Raises:
            asyncio.TimeoutError: If device did not disconnect with 10 seconds.

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
        if self._requester:
            event = asyncio.Event()
            self._disconnect_events.append(event)
            try:
                self._requester.Dispose()
                await asyncio.wait_for(event.wait(), timeout=10)
            finally:
                self._disconnect_events.remove(event)

        # Set device info to None as well.
        self._device_info = None

        # Finally, dispose of the Bleak Bridge as well.
        self._bridge.Dispose()
        self._bridge = None

        return True