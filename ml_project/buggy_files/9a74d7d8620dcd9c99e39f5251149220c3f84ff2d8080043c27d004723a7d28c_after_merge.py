    def close(self):
        """
        Cleanup and (if leave=False) close the progressbar.
        """
        if self.disable:
            return

        # Prevent multiple closures
        self.disable = True

        # decrement instance pos and remove from internal set
        pos = self.pos
        self._decr_instances(self)

        # GUI mode
        if not hasattr(self, "sp"):
            return

        # annoyingly, _supports_unicode isn't good enough
        def fp_write(s):
            self.fp.write(_unicode(s))

        try:
            fp_write('')
        except ValueError as e:
            if 'closed' in str(e):
                return
            raise  # pragma: no cover

        if pos:
            self.moveto(pos)

        if self.leave:
            if self.last_print_n < self.n:
                cur_t = self._time()
                # stats for overall rate (no weighted average)
                self.sp(self.format_meter(
                    self.n, self.total, cur_t - self.start_t,
                    (self.dynamic_ncols(self.fp) if self.dynamic_ncols
                     else self.ncols),
                    self.desc, self.ascii, self.unit, self.unit_scale, None,
                    self.bar_format, self.postfix, self.unit_divisor))
            if pos:
                self.moveto(-pos)
            else:
                fp_write('\n')
        else:
            self.sp('')  # clear up last bar
            if pos:
                self.moveto(-pos)
            else:
                fp_write('\r')