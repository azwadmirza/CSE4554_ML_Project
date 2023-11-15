    def populate(self):
        super(Interfaces, self).populate()

        self.facts['all_ipv4_addresses'] = list()
        self.facts['all_ipv6_addresses'] = list()

        data = self.responses[0]
        self.facts['interfaces'] = self.populate_interfaces(data)

        data = self.responses[1]
        if data:
            self.facts['neighbors'] = self.populate_neighbors(data['lldpNeighbors'])