def mpl_rc_context(f):
    """
    Decorator for MPLPlot methods applying the matplotlib rc params
    in the plots fig_rcparams while when method is called.
    """
    def wrapper(self, *args, **kwargs):
        with _rc_context(self.fig_rcparams):
            return f(self, *args, **kwargs)
    return wrapper