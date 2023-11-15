def mpl_rc_context(f):
    """
    Applies matplotlib rc params while when method is called.
    """
    def wrapper(self, *args, **kwargs):
        with mpl.rc_context(rc=self.fig_rcparams):
            return f(self, *args, **kwargs)
    return wrapper