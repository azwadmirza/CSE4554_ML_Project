    def getfield(self, pkt, s):
        tmp_len = self.length_from(pkt) or 0
        if tmp_len <= 0:
            return s, []
        return s[tmp_len:], self.m2i(pkt, s[:tmp_len])