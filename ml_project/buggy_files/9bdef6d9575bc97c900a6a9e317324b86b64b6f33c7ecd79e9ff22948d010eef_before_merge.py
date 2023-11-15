    def _on_service_property_changed(self, _service, key, value):
        if key == "Connected":
            self.Generate()