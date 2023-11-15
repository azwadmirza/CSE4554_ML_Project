    def i2m(self, pkt, s):
        if not isinstance(s, bytes):
            s = bytes_encode(s)
        s = b"".join(chb(len(x)) + x for x in s.split(b"."))
        return s