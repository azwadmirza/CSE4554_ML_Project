    def get_input_output(self, pin, port, attrs, invert):
        self._check_feature("single-ended input/output", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        m = Module()
        self._get_io_buffer(m, pin, port, attrs, i_invert=invert, o_invert=invert)
        return m