    def __str__(self):
        str_ports = []
        if self.tagged:
            str_ports.append('tagged: %s' % ','.join([str(p) for p in self.tagged]))
        if self.untagged:
            str_ports.append('untagged: %s' % ','.join([str(p) for p in self.untagged]))
        return 'VLAN %s vid:%s %s' % (self.name, self.vid, ' '.join(str_ports))