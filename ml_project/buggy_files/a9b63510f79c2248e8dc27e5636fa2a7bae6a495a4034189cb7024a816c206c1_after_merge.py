    def decode(self, code):
        n = len(code)
        if n:
            return struct.unpack('>%dB' % n, code)
        else:
            return ()