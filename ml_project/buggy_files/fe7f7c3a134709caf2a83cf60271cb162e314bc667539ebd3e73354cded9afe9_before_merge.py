    def _on_device_property_changed(self, device, key, value):
        if key == "Connected" and not value:
            self.terminate_all_scripts(device.Address)