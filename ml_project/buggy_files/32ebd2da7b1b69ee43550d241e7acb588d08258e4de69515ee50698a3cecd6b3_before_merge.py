    def get_diff_input(self, pin, p_port, n_port, attrs, invert):
        self._check_feature("differential input", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        m = Module()
        # See comment in should_skip_port_component above.
        self._get_io_buffer(m, pin, p_port, attrs, i_invert=invert)
        return m