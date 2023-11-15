    def reset_ports(self, ports):
        """Reset tagged and untagged port lists."""
        sorted_ports = sorted(ports, key=lambda i: i.number)
        self.tagged = tuple([port for port in sorted_ports if self in port.tagged_vlans])
        self.untagged = tuple([port for port in sorted_ports if self == port.native_vlan])