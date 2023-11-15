    def __init__(self, obj, func, broadcast, raw, reduce, result_type,
                 ignore_failures, args, kwds):
        self.obj = obj
        self.raw = raw
        self.ignore_failures = ignore_failures
        self.args = args or ()
        self.kwds = kwds or {}

        if result_type not in [None, 'reduce', 'broadcast', 'expand']:
            raise ValueError("invalid value for result_type, must be one "
                             "of {None, 'reduce', 'broadcast', 'expand'}")

        if broadcast is not None:
            warnings.warn("The broadcast argument is deprecated and will "
                          "be removed in a future version. You can specify "
                          "result_type='broadcast' to broadcast the result "
                          "to the original dimensions",
                          FutureWarning, stacklevel=4)
            if broadcast:
                result_type = 'broadcast'

        if reduce is not None:
            warnings.warn("The reduce argument is deprecated and will "
                          "be removed in a future version. You can specify "
                          "result_type='reduce' to try to reduce the result "
                          "to the original dimensions",
                          FutureWarning, stacklevel=4)
            if reduce:

                if result_type is not None:
                    raise ValueError(
                        "cannot pass both reduce=True and result_type")

                result_type = 'reduce'

        self.result_type = result_type

        # curry if needed
        if kwds or args and not isinstance(func, np.ufunc):
            def f(x):
                return func(x, *args, **kwds)
        else:
            f = func

        self.f = f

        # results
        self.result = None
        self.res_index = None
        self.res_columns = None