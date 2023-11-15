    def reset_ports(self, ports):
        """Reset tagged and untagged port lists."""
        self.tagged = tuple([port for port in ports if self in port.tagged_vlans])
        self.untagged = tuple([port for port in ports if self == port.native_vlan])