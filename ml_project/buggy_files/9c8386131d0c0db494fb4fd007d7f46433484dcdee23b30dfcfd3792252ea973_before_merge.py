    def populate(self):
        data = self.run('show version', output='json')
        if data:
            self.facts.update(self.transform_dict(data, self.VERSION_MAP))

        data = self.run('show interface', output='json')
        if data:
            self.facts['_interfaces_list'] = self.parse_interfaces(data)

        data = self.run('show vlan brief', output='json')
        if data:
            self.facts['_vlan_list'] = self.parse_vlans(data)

        data = self.run('show module', output='json')
        if data:
            self.facts['_module'] = self.parse_module(data)

        data = self.run('show environment', output='json')
        if data:
            self.facts['_fan_info'] = self.parse_fan_info(data)
            self.facts['_power_supply_info'] = self.parse_power_supply_info(data)