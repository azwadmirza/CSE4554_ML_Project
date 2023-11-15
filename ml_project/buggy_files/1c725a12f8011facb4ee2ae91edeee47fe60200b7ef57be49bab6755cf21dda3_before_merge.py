    def iter_differential_pins(self):
        for res, pin, port, attrs in self._ports:
            if pin is None:
                continue
            if isinstance(res.ios[0], DiffPairs):
                yield pin, port.p, port.n, attrs, res.ios[0].invert