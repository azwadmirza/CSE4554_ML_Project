    def _on_network_prop_changed(self, _network, key, value, _path):
        if key == "Interface":
            if value != "":
                self.dhcp_acquire(value)