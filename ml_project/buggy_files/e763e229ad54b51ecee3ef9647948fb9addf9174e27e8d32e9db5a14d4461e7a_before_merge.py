def _disable_method(fcn, msg=None):
    if msg is None:
        msg = 'access %s on' % (fcn.__name__,)
    def impl(self, *args, **kwds):
        raise RuntimeError(
            "Cannot %s %s '%s' before it has been constructed (initialized)."
            % (msg, type(self).__name__, self.name))

    # functools.wraps doesn't preserve the function signature until
    # Python 3.4.  For backwards compatability with Python 2.x, we will
    # create a temporary (lambda) function using eval that matches the
    # function signature passed in and calls the generic impl() function
    args = inspect.formatargspec(*inspect.getargspec(fcn))
    impl_args = eval('lambda %s: impl%s' % (args[1:-1], args), {'impl': impl})
    return functools.wraps(fcn)(impl_args)