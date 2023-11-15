    def wrapper(self, *args, **kwargs):
        with mpl.rc_context(rc=self.fig_rcparams):
            return f(self, *args, **kwargs)