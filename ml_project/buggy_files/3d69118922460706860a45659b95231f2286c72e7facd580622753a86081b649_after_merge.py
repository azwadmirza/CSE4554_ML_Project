    def load_current_config(self):
        # called in base class in run function
        self._os_version = self._get_os_version()
        self._current_config = dict()
        vlan_config = self._get_vlan_config()
        if not vlan_config:
            return
        for vlan_id, vlan_data in iteritems(vlan_config):
            try:
                vlan_id = int(vlan_id)
            except ValueError:
                continue
            self._current_config[vlan_id] = \
                self._create_vlan_data(vlan_id, vlan_data)