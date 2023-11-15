    def _on_properties_changed(self, interface_name, changed_properties, _invalidated_properties):
        if interface_name == self._interface_name:
            for name, value in changed_properties.items():
                self._on_property_changed(name, value)