    def _on_device_property_changed(self, _device, key, value, _path):
        if key == "Connected":
            if value:
                self.num_connections += 1
            else:
                self.num_connections -= 1

            if (self.num_connections > 0 and not self.active) or (self.num_connections == 0 and self.active):
                self.Applet.Plugins.StatusIcon.IconShouldChange()

            self.update_statusicon()