    def post_build(self, p, pay):
        p += pay
        dataofs = self.dataofs
        if dataofs is None:
            dataofs = 5 + ((len(self.get_field("options").i2m(self, self.options)) + 3) // 4)  # noqa: E501
            p = p[:12] + chb((dataofs << 4) | orb(p[12]) & 0x0f) + p[13:]
        if self.chksum is None:
            if isinstance(self.underlayer, IP):
                ck = in4_chksum(socket.IPPROTO_TCP, self.underlayer, p)
                p = p[:16] + struct.pack("!H", ck) + p[18:]
            elif conf.ipv6_enabled and isinstance(self.underlayer, scapy.layers.inet6.IPv6) or isinstance(self.underlayer, scapy.layers.inet6._IPv6ExtHdr):  # noqa: E501
                ck = scapy.layers.inet6.in6_chksum(socket.IPPROTO_TCP, self.underlayer, p)  # noqa: E501
                p = p[:16] + struct.pack("!H", ck) + p[18:]
            else:
                warning("No IP underlayer to compute checksum. Leaving null.")
        return p