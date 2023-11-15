    def get_tristate(self, pin, port, attrs, invert):
        self._check_feature("single-ended tristate", pin, attrs,
                            valid_xdrs=(0, 1, 2), valid_attrs=True)
        if pin.xdr == 1:
            port.attrs["useioff"] = 1

        m = Module()
        m.submodules[pin.name] = Instance("altiobuf_out",
            p_enable_bus_hold="FALSE",
            p_number_of_channels=pin.width,
            p_use_differential_mode="FALSE",
            p_use_oe="TRUE",
            i_datain=self._get_oreg(m, pin, invert),
            o_dataout=port,
            i_oe=self._get_oereg(m, pin)
        )
        return m