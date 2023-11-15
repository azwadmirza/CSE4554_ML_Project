    def reset(self, total=None):
        """
        Resets to 0 iterations for repeated use.

        Consider combining with `leave=True`.

        Parameters
        ----------
        total  : int or float, optional. Total to use for the new bar.
        """
        self.last_print_n = self.n = 0
        self.last_print_t = self.start_t = self._time()
        self._ema_dn = EMA(self.smoothing)
        self._ema_dt = EMA(self.smoothing)
        self._ema_miniters = EMA(self.smoothing)
        if total is not None:
            self.total = total
        self.refresh()