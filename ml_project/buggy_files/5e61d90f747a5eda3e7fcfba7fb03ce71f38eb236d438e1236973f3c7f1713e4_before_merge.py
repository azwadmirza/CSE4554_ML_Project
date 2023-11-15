    def __str__(self):
        port_list = tuple([str(x) for x in self.get_ports()])
        ports = ','.join(port_list)
        return 'VLAN %s vid:%s ports:%s' % (self.name, self.vid, ports)