    def _try_aggregate_string_function(self, arg, *args, **kwargs):
        """
        if arg is a string, then try to operate on it:
        - try to find a function (or attribute) on ourselves
        - try to find a numpy function
        - raise

        """
        assert isinstance(arg, compat.string_types)

        f = getattr(self, arg, None)
        if f is not None:
            if callable(f):
                return f(*args, **kwargs)

            # people may try to aggregate on a non-callable attribute
            # but don't let them think they can pass args to it
            assert len(args) == 0
            assert len([kwarg for kwarg in kwargs
                        if kwarg not in ['axis', '_level']]) == 0
            return f

        f = getattr(np, arg, None)
        if f is not None:
            return f(self, *args, **kwargs)

        raise ValueError("{} is an unknown string function".format(arg))