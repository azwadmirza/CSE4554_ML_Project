    def _on_network_property_changed(self, _network, key, value, path):
        if key == "Interface" and value != "":
            d = BluezDevice(path)
            d = Device(d)
            self.monitor_interface(Monitor, d, value)