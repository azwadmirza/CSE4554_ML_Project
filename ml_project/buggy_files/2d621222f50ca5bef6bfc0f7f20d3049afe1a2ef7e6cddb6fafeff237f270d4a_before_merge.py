    def _on_network_property_changed(self, network, key, value):
        if key == "Interface" and value != "":
            d = BluezDevice(network.get_object_path())
            d = Device(d)
            self.monitor_interface(Monitor, d, value)