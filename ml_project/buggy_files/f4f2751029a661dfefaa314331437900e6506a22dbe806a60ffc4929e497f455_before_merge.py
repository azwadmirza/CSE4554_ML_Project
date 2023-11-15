    def read_packet(self, size=MTU):
        rp = super(PcapNgReader, self).read_packet(size=size)
        if rp is None:
            raise EOFError
        s, (linktype, tsresol, tshigh, tslow, wirelen) = rp
        try:
            p = conf.l2types[linktype](s)
        except KeyboardInterrupt:
            raise
        except Exception:
            if conf.debug_dissector:
                raise
            p = conf.raw_layer(s)
        if tshigh is not None:
            p.time = EDecimal((tshigh << 32) + tslow) / tsresol
        p.wirelen = wirelen
        return p