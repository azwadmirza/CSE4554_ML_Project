    def _on_property_changed(self, _adapter, key, value, _path):
        if key == "Discovering":
            if not value and self.discovering:
                self.StopDiscovery()

        self.emit("adapter-property-changed", self.Adapter, (key, value))