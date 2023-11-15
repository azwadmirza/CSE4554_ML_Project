    def load_current_config(self):
        # called in base class in run function
        self._os_version = self._get_os_version()
        self._current_config = dict()
        switchports_config = self._get_switchport_config()
        if not switchports_config:
            return
        for if_name, if_data in iteritems(switchports_config):
            self._current_config[if_name] = \
                self._create_switchport_data(if_name, if_data)