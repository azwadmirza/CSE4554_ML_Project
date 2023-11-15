        def _ConnectionStatusChanged_Handler(sender, args):
            logger.debug(
                "_ConnectionStatusChanged_Handler: %d", sender.ConnectionStatus
            )
            if sender.ConnectionStatus == BluetoothConnectionStatus.Disconnected:
                if self._disconnected_callback:
                    loop.call_soon_threadsafe(self._disconnected_callback, self)

                for e in self._disconnect_events:
                    loop.call_soon_threadsafe(e.set)

                def handle_disconnect():
                    self._requester = None

                loop.call_soon_threadsafe(handle_disconnect)