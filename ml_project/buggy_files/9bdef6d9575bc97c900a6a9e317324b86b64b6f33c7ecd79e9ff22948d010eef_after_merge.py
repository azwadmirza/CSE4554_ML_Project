    def _on_service_property_changed(self, _service, key, _value, _path):
        if key == "Connected":
            self.Generate()