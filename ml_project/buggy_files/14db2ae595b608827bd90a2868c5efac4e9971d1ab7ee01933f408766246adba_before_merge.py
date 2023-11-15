    def open(self):
        self._device.open()
        self.get_version()
        self.get_target_voltage()