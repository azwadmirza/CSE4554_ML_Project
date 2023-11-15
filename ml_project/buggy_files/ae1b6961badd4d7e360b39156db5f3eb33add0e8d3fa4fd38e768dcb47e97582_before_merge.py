    def get_diff_output(self, pin, p_port, n_port, attrs, invert):
        self._check_feature("differential output", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        m = Module()
        # Note that the non-inverting output pin is not driven the same way as a regular
        # output pin. The inverter introduces a delay, so for a non-inverting output pin,
        # an identical delay is introduced by instantiating a LUT. This makes the waveform
        # perfectly symmetric in the xdr=0 case.
        self._get_io_buffer(m, pin, p_port, attrs, o_invert=    invert, invert_lut=True)
        self._get_io_buffer(m, pin, n_port, attrs, o_invert=not invert, invert_lut=True)
        return m