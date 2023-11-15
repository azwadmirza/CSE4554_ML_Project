    def m2i(self, pkt, val):
        ret = []
        for v in val:
            byte = orb(v)
            left = byte >> 4
            right = byte & 0xf
            if left == 0xf:
                ret.append(TBCD_TO_ASCII[right:right + 1])
            else:
                ret += [
                    TBCD_TO_ASCII[right:right + 1],
                    TBCD_TO_ASCII[left:left + 1]
                ]
        return b"".join(ret)