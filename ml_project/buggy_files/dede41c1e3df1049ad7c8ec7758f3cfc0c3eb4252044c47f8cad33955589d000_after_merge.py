    def addfield(self, pkt, s, val):
        len_pkt = self.length_from(pkt)
        if len_pkt is None:
            return s + self.i2m(pkt, val)
        return s + struct.pack("%is" % len_pkt, self.i2m(pkt, val))