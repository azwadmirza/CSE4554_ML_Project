    def i2m(self, pkt, val):
        if not isinstance(val, bytes):
            val = bytes_encode(val)
        ret_string = b""
        for i in range(0, len(val), 2):
            tmp = val[i:i + 2]
            if len(tmp) == 2:
                ret_string += chb(int(tmp[::-1], 16))
            else:
                ret_string += chb(int(b"F" + tmp[:1], 16))
        return ret_string