    def _on_device_property_changed(self, device, key, value):
        iter = self.find_device_by_path(device.get_object_path())

        if iter != None:
            dev = self.get(iter, "device")["device"]
            self.row_update_event(iter, key, value)

            self.emit("device-property-changed", dev, iter, (key, value))

            if key == "Connected":
                if value:
                    self.monitor_power_levels(dev)
                else:
                    r = Gtk.TreeRowReference.new(self.get_model(), self.props.model.get_path(iter))
                    self.level_setup_event(r, dev, None)

            elif key == "Paired":
                if value and dev.Temp:
                    dev.Temp = False