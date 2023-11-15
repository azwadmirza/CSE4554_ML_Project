    def populate(self):
        data = None

        try:
            data = self.run('show version')
        except ConnectionError:
            data = self.run('show version', output='json')
        if data:
            if isinstance(data, dict):
                self.facts.update(self.transform_dict(data, self.VERSION_MAP))
            else:
                self.facts['_hostname'] = self.parse_hostname(data)
                self.facts['_os'] = self.parse_os(data)
                self.facts['_platform'] = self.parse_platform(data)

        try:
            data = self.run('show interface', output='json')
        except ConnectionError:
            data = self.run('show interface')
        if data:
            if isinstance(data, dict):
                self.facts['_interfaces_list'] = self.parse_structured_interfaces(data)
            else:
                self.facts['_interfaces_list'] = self.parse_interfaces(data)

        try:
            data = self.run('show vlan brief', output='json')
        except ConnectionError:
            data = self.run('show vlan brief')
        if data:
            if isinstance(data, dict):
                self.facts['_vlan_list'] = self.parse_structured_vlans(data)
            else:
                self.facts['_vlan_list'] = self.parse_vlans(data)

        try:
            data = self.run('show module', output='json')
        except ConnectionError:
            data = self.run('show module')
        if data:
            if isinstance(data, dict):
                self.facts['_module'] = self.parse_structured_module(data)
            else:
                self.facts['_module'] = self.parse_module(data)

        try:
            data = self.run('show environment fan', output='json')
        except ConnectionError:
            data = self.run('show environment fan')
        if data:
            if isinstance(data, dict):
                self.facts['_fan_info'] = self.parse_structured_fan_info(data)
            else:
                self.facts['_fan_info'] = self.parse_fan_info(data)

        try:
            data = self.run('show environment power', output='json')
        except ConnectionError:
            data = self.run('show environment power')
        if data:
            if isinstance(data, dict):
                self.facts['_power_supply_info'] = self.parse_structured_power_supply_info(data)
            else:
                self.facts['_power_supply_info'] = self.parse_power_supply_info(data)