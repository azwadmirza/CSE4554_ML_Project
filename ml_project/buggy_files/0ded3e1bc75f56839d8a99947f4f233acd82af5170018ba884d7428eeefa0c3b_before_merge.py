    def i2m(self, pkt, val):
        val = str(val)
        ret_string = ""
        for i in range(0, len(val), 2):
            tmp = val[i:i + 2]
            if len(tmp) == 2:
                ret_string += chr(int(tmp[1] + tmp[0], 16))
            else:
                ret_string += chr(int("F" + tmp[0], 16))
        return ret_string