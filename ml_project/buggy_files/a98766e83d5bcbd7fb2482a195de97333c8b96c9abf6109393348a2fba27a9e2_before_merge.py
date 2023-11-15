    def _on_property_changed(self, key, value):
        dprint(self.get_object_path(), key, value)
        self.emit('property-changed', key, value)