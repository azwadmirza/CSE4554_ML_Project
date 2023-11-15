    def on_adapter_property_changed(self, list, adapter, kv):
        (key, value) = kv
        if key == "Name" or key == "Alias":
            self.generate_adapter_menu()
        elif key == "Discovering":
            if self.Search:
                if value:
                    self.Search.props.sensitive = False
                else:
                    self.Search.props.sensitive = True