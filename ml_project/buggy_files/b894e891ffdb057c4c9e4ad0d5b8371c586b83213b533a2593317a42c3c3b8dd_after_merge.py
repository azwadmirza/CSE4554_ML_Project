    def read_packet(self, size=MTU):
        rp = super(PcapReader, self).read_packet(size=size)
        if rp is None:
            raise EOFError
        s, pkt_info = rp

        try:
            p = self.LLcls(s)
        except KeyboardInterrupt:
            raise
        except Exception:
            if conf.debug_dissector:
                from scapy.sendrecv import debug
                debug.crashed_on = (self.LLcls, s)
                raise
            from scapy.packet import Raw
            p = (conf.raw_layer or Raw)(s)
        power = Decimal(10) ** Decimal(-9 if self.nano else -6)
        p.time = EDecimal(pkt_info.sec + power * pkt_info.usec)
        p.wirelen = pkt_info.wirelen
        return p