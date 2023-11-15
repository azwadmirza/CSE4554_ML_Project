    def _create_switchport_data(self, if_name, if_data):
        return {
            'name': if_name,
            'mode': self.get_config_attr(if_data, 'Mode'),
            'access_vlan': self.get_access_vlan(if_data),
            'trunk_allowed_vlans': self.get_allowed_vlans(if_data)
        }