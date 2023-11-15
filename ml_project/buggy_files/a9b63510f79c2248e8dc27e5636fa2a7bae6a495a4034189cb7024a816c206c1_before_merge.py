    def decode(self, code):
        n = len(code)//2
        if n:
            return struct.unpack('>%dH' % n, code)
        else:
            return ()