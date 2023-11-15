    def _do_start_app(self):
        """Overrides superclass."""
        self._adb.shell(_LAUNCH_CMD % self.device_port)