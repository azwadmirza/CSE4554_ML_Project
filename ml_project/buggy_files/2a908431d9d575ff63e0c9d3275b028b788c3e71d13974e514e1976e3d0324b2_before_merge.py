    def iter_single_ended_pins(self):
        for res, pin, port, attrs in self._ports:
            if pin is None:
                continue
            if isinstance(res.ios[0], Pins):
                yield pin, port.io, attrs, res.ios[0].invert