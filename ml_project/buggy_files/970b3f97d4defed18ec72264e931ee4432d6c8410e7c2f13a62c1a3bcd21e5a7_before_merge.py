        def _ConnectionStatusChanged_Handler(sender, args):
            logger.debug(
                "_ConnectionStatusChanged_Handler: %d", sender.ConnectionStatus
            )
            if (
                sender.ConnectionStatus == BluetoothConnectionStatus.Disconnected
                and self._disconnected_callback
            ):
                loop.call_soon_threadsafe(self._disconnected_callback, self)