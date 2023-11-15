    def post_build(self, p, pay):
        if self.domnamelen is None:
            domnamelen = len(self.domname.strip(b"\x00"))
            p = p[:3] + chr(domnamelen & 0xff) + p[4:]

        p += pay

        return p