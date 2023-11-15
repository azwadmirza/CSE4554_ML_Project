    def _try_aggregate_string_function(self, arg, *args, **kwargs):
        """
        if arg is a string, then try to operate on it:
        - try to find a function on ourselves
        - try to find a numpy function
        - raise

        """
        assert isinstance(arg, compat.string_types)

        f = getattr(self, arg, None)
        if f is not None:
            return f(*args, **kwargs)

        f = getattr(np, arg, None)
        if f is not None:
            return f(self, *args, **kwargs)

        raise ValueError("{} is an unknown string function".format(arg))