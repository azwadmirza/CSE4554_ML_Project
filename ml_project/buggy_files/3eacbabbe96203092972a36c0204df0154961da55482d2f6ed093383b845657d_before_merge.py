    def disconnect(self, **kwargs):
        """Disconnect from the device."""
        self._close()
        super().disconnect()
        self.device.release()