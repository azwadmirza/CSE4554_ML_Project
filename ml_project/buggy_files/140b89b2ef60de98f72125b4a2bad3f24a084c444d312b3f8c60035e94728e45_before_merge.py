    def load_current_config(self):
        self._current_config = dict()
        config = self._get_interfaces_config()
        if not config:
            return

        for item in config:
            name = self.get_if_name(item)
            self._current_config[name] = self._create_if_data(name, item)