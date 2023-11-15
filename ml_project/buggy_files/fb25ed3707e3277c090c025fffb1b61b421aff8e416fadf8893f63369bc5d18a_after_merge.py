    def get_input(self, pin, port, attrs, invert):
        self._check_feature("single-ended input", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        m = Module()
        self._get_io_buffer(m, pin, port.io, attrs, i_invert=invert)
        return m