    def alloc_color(self, color):
        """
            Flexible color allocation.
        """
        try:
            return self.conn.conn.core.AllocNamedColor(
                self.cid, len(color), color
            ).reply()
        except xcffib.xproto.NameError:

            def x8to16(i):
                return 0xffff * (i & 0xff) // 0xff
            r = x8to16(int(color[-6] + color[-5], 16))
            g = x8to16(int(color[-4] + color[-3], 16))
            b = x8to16(int(color[-2] + color[-1], 16))
            return self.conn.conn.core.AllocColor(self.cid, r, g, b).reply()