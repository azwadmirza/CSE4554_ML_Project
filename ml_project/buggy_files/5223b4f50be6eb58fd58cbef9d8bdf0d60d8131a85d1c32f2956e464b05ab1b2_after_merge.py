    def __repr__(self, elapsed=None):
        return self.format_meter(
            self.n, self.total,
            elapsed if elapsed is not None else self._time() - self.start_t,
            self.dynamic_ncols(self.fp) if self.dynamic_ncols else self.ncols,
            self.desc, self.ascii, self.unit,
            self.unit_scale, 1 / self.avg_time if self.avg_time else None,
            self.bar_format, self.postfix, self.unit_divisor)