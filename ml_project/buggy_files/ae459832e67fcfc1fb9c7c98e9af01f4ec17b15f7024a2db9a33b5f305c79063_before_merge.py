    def prepare(self, elaboratable, name="top", **kwargs):
        assert not self._prepared
        self._prepared = True

        fragment = Fragment.get(elaboratable, self)
        fragment = SampleLowerer()(fragment)
        fragment._propagate_domains(self.create_missing_domain, platform=self)
        fragment = DomainLowerer()(fragment)

        def add_pin_fragment(pin, pin_fragment):
            pin_fragment = Fragment.get(pin_fragment, self)
            if not isinstance(pin_fragment, Instance):
                pin_fragment.flatten = True
            fragment.add_subfragment(pin_fragment, name="pin_{}".format(pin.name))

        for pin, port, attrs, invert in self.iter_single_ended_pins():
            if pin.dir == "i":
                add_pin_fragment(pin, self.get_input(pin, port, attrs, invert))
            if pin.dir == "o":
                add_pin_fragment(pin, self.get_output(pin, port, attrs, invert))
            if pin.dir == "oe":
                add_pin_fragment(pin, self.get_tristate(pin, port, attrs, invert))
            if pin.dir == "io":
                add_pin_fragment(pin, self.get_input_output(pin, port, attrs, invert))

        for pin, p_port, n_port, attrs, invert in self.iter_differential_pins():
            if pin.dir == "i":
                add_pin_fragment(pin, self.get_diff_input(pin, p_port, n_port, attrs, invert))
            if pin.dir == "o":
                add_pin_fragment(pin, self.get_diff_output(pin, p_port, n_port, attrs, invert))
            if pin.dir == "oe":
                add_pin_fragment(pin, self.get_diff_tristate(pin, p_port, n_port, attrs, invert))
            if pin.dir == "io":
                add_pin_fragment(pin,
                    self.get_diff_input_output(pin, p_port, n_port, attrs, invert))

        fragment._propagate_ports(ports=self.iter_ports(), all_undef_as_ports=False)
        return self.toolchain_prepare(fragment, name, **kwargs)