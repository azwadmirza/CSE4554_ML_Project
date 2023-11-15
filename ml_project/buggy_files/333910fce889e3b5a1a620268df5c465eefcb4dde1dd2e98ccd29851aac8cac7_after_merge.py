    def wrapper(self, *args, **kwargs):
        with _rc_context(self.fig_rcparams):
            return f(self, *args, **kwargs)