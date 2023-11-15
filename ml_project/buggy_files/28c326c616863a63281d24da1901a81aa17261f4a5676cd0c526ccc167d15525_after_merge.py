    def _create_vlan_data(self, vlan_id, vlan_data):
        if self._os_version >= self.ONYX_API_VERSION:
            vlan_data = vlan_data[0]
        return {
            'vlan_id': vlan_id,
            'name': self.get_config_attr(vlan_data, 'Name')
        }