    def addfield(self, pkt, s, val):
        len_pkt = self.length_from(pkt)
        return s + struct.pack("%is" % len_pkt, self.i2m(pkt, val))