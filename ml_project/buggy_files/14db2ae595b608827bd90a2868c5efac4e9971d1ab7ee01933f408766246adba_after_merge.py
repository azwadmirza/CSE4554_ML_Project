    def open(self):
        self._device.open()
        self.enter_idle()
        self.get_version()
        self.get_target_voltage()