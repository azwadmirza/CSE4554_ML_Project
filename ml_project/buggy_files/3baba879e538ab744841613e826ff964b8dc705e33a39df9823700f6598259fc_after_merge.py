    def _set_params_item(self, item, name=None):
        self.params.append(item)
        if name:
            self.params._add_name(name)