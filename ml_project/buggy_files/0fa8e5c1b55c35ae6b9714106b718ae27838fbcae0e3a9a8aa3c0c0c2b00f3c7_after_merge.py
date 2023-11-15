    def get_diff_input_output(self, pin, port, attrs, invert):
        self._check_feature("differential input/output", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        if pin.xdr == 1:
            port.p.attrs["useioff"] = 1
            port.n.attrs["useioff"] = 1

        m = Module()
        m.submodules[pin.name] = Instance("altiobuf_bidir",
            p_enable_bus_hold="FALSE",
            p_number_of_channels=pin.width,
            p_use_differential_mode="TRUE",
            i_datain=self._get_oreg(m, pin, invert),
            io_dataio=port.p,
            io_dataio_b=port.n,
            o_dataout=self._get_ireg(m, pin, invert),
            i_oe=self._get_oereg(m, pin),
        )
        return m