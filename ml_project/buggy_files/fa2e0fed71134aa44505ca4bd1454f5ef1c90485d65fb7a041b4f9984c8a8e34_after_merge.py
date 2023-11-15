    def populate(self):
        self.facts['all_ipv4_addresses'] = list()
        self.facts['all_ipv6_addresses'] = list()
        data = None

        try:
            data = self.run('show interface', output='json')
        except ConnectionError:
            data = self.run('show interface')
        if data:
            if isinstance(data, dict):
                self.facts['interfaces'] = self.populate_structured_interfaces(data)
            else:
                interfaces = self.parse_interfaces(data)
                self.facts['interfaces'] = self.populate_interfaces(interfaces)

        if self.ipv6_structure_op_supported():
            try:
                data = self.run('show ipv6 interface', output='json')
            except ConnectionError:
                data = self.run('show ipv6 interface')
        else:
            data = None
        if data:
            if isinstance(data, dict):
                self.populate_structured_ipv6_interfaces(data)
            else:
                interfaces = self.parse_interfaces(data)
                self.populate_ipv6_interfaces(interfaces)

        data = self.run('show lldp neighbors')
        if data:
            self.facts['neighbors'] = self.populate_neighbors(data)

        try:
            data = self.run('show cdp neighbors detail', output='json')
        except ConnectionError:
            data = self.run('show cdp neighbors detail')
        if data:
            if isinstance(data, dict):
                self.facts['neighbors'] = self.populate_structured_neighbors_cdp(data)
            else:
                self.facts['neighbors'] = self.populate_neighbors_cdp(data)