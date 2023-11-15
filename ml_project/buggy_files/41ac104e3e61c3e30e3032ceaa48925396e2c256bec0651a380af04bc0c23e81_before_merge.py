    def load_current_config(self):
        # called in base class in run function
        self._current_config = dict()
        if_types = set([if_obj['if_type'] for if_obj in self._required_config])
        for if_type in if_types:
            if_config = self._get_interfaces_config(if_type)
            if not if_config:
                continue
            self._parse_interfaces_config(if_type, if_config)