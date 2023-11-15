    def __repr__(self):
        return self.format_meter(self.n, self.total,
                                 time() - self.last_print_t,
                                 self.ncols, self.desc, self.ascii, self.unit,
                                 self.unit_scale, 1 / self.avg_time
                                 if self.avg_time else None, self.bar_format)