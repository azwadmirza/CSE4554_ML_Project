    def _on_property_changed(self, key, value, path):
        dprint(path, key, value)
        self.emit('property-changed', key, value, path)