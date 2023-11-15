    def _on_device_property_changed(self, _device, key, value, path):
        if key == "Connected":
            klass = bluez.Device(path).get_properties()["Class"] & 0x1fff

            if klass == 0x504 or klass == 0x508:
                if value:
                    self.xdg_screensaver("suspend")
                else:
                    self.xdg_screensaver("resume")