    def post_build(self, p, pay):
        vlannamelen = 4 * ((len(self.vlanname) + 3) // 4)

        if self.len is None:
            tmp_len = vlannamelen + 12
            p = chr(tmp_len & 0xff) + p[1:]

        # Pad vlan name with zeros if vlannamelen > len(vlanname)
        tmp_len = vlannamelen - len(self.vlanname)
        if tmp_len != 0:
            p += b"\x00" * tmp_len

        p += pay

        return p