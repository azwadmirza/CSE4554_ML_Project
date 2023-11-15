    def i2m(self, pkt, s):
        s = b"".join(chb(len(x)) + x for x in s.split("."))
        return s