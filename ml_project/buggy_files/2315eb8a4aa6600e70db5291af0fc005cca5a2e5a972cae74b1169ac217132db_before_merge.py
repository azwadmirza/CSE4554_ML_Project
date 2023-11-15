    def getfield(self, pkt, s):
        tmp_len = self.length_from(pkt)
        if tmp_len is None:
            return s, []
        return s[tmp_len:], self.m2i(pkt, s[:tmp_len])