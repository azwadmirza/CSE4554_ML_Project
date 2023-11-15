    def _on_device_property_changed(self, _device, key, value, path):
        if key == "Connected" and not value:
            self.terminate_all_scripts(Device(path).Address)