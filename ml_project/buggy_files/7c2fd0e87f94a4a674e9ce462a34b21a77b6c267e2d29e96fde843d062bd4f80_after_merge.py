    def get_input_output(self, pin, port, attrs, invert):
        self._check_feature("single-ended input/output", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        if pin.xdr == 1:
            port.attrs["useioff"] = 1

        m = Module()
        m.submodules[pin.name] = Instance("altiobuf_bidir",
            p_enable_bus_hold="FALSE",
            p_number_of_channels=pin.width,
            p_use_differential_mode="FALSE",
            i_datain=self._get_oreg(m, pin, invert),
            io_dataio=port.io,
            o_dataout=self._get_ireg(m, pin, invert),
            i_oe=self._get_oereg(m, pin),
        )
        return m