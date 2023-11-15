    def get_diff_input(self, pin, port, attrs, invert):
        self._check_feature("differential input", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        if pin.xdr == 1:
            port.p.attrs["useioff"] = 1
            port.n.attrs["useioff"] = 1

        m = Module()
        m.submodules[pin.name] = Instance("altiobuf_in",
            p_enable_bus_hold="FALSE",
            p_number_of_channels=pin.width,
            p_use_differential_mode="TRUE",
            i_datain=port.p,
            i_datain_b=port.n,
            o_dataout=self._get_ireg(m, pin, invert)
        )
        return m