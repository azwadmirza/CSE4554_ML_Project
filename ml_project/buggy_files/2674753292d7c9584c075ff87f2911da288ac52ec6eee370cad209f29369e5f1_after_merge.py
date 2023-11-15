    def get_diff_output(self, pin, port, attrs, invert):
        self._check_feature("differential output", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        if pin.xdr == 1:
            port.p.attrs["useioff"] = 1
            port.n.attrs["useioff"] = 1

        m = Module()
        m.submodules[pin.name] = Instance("altiobuf_out",
            p_enable_bus_hold="FALSE",
            p_number_of_channels=pin.width,
            p_use_differential_mode="TRUE",
            p_use_oe="FALSE",
            i_datain=self._get_oreg(m, pin, invert),
            o_dataout=port.p,
            o_dataout_b=port.n,
        )
        return m