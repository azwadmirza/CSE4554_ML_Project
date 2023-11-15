    def _parse_interfaces_config(self, if_type, if_config):
        if self._os_version < self.ONYX_API_VERSION:
            for if_data in if_config:
                if_name = self.get_config_attr(if_data, 'header')
                self._get_if_attributes(if_type, if_name, if_data)
        else:
            for if_config_item in if_config:
                for if_name, if_data in iteritems(if_config_item):
                    if_data = if_data[0]
                    self._get_if_attributes(if_type, if_name, if_data)