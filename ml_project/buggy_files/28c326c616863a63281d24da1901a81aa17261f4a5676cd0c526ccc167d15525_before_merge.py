    def _create_vlan_data(self, vlan_id, vlan_data):
        return {
            'vlan_id': vlan_id,
            'name': self.get_config_attr(vlan_data, 'Name')
        }