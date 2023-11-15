    def populate(self):
        self.facts['all_ipv4_addresses'] = list()
        self.facts['all_ipv6_addresses'] = list()

        data = self.run('show interface', output='json')
        if data:
            self.facts['interfaces'] = self.populate_interfaces(data)

        data = self.run('show ipv6 interface', output='json') if self.ipv6_structure_op_supported() else None
        if data and not isinstance(data, string_types):
            self.parse_ipv6_interfaces(data)

        data = self.run('show lldp neighbors')
        if data:
            self.facts['neighbors'] = self.populate_neighbors(data)

        data = self.run('show cdp neighbors detail', output='json')
        if data:
            self.facts['neighbors'] = self.populate_neighbors_cdp(data)