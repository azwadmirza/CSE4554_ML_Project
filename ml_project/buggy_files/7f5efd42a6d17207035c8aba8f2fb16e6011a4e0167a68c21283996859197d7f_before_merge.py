    def format_dict(self):
        """Public API for read-only member access."""
        if self.dynamic_ncols:
            self.ncols, self.nrows = self.dynamic_ncols(self.fp)
        ncols, nrows = self.ncols, self.nrows
        return {
            'n': self.n, 'total': self.total,
            'elapsed': self._time() - self.start_t if hasattr(self, 'start_t') else 0,
            'ncols': ncols, 'nrows': nrows, 'prefix': self.desc, 'ascii': self.ascii,
            'unit': self.unit, 'unit_scale': self.unit_scale,
            'rate': self._ema_dn() / self._ema_dt() if self._ema_dt() else None,
            'bar_format': self.bar_format, 'postfix': self.postfix,
            'unit_divisor': self.unit_divisor, 'initial': self.initial,
            'colour': self.colour}