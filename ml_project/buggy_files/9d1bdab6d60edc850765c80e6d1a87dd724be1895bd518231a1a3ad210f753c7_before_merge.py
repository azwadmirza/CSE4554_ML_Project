    def apply(self, func, convert_dtype=True, args=(), **kwds):
        # apply and aggregate have slightly different behaviors, so we have to use
        # each one separately to determine the correct return type. In the case of
        # `agg`, the axis is set, but it is not required for the computation, so we use
        # it to determine which function to run.
        if kwds.pop("axis", None) is not None:
            apply_func = "agg"
        else:
            apply_func = "apply"

        # This is the simplest way to determine the return type, but there are checks
        # in pandas that verify that some results are created. This is a challenge for
        # empty DataFrames, but fortunately they only happen when the `func` type is
        # a list or a dictionary, which means that the return type won't change from
        # type(self), so we catch that error and use `self.__name__` for the return
        # type.
        # Because a `Series` cannot be empty in pandas, we create a "dummy" `Series` to
        # do the error checking and determining the return type.
        try:
            return_type = type(
                getattr(pandas.Series([""], index=self.index[:1]), apply_func)(
                    func, *args, **kwds
                )
            ).__name__
        except Exception:
            return_type = self.__name__
        if (
            isinstance(func, str)
            or is_list_like(func)
            or return_type not in ["DataFrame", "Series"]
        ):
            query_compiler = super(Series, self).apply(func, *args, **kwds)
        else:
            # handle ufuncs and lambdas
            if kwds or args and not isinstance(func, np.ufunc):

                def f(x):
                    return func(x, *args, **kwds)

            else:
                f = func
            with np.errstate(all="ignore"):
                if isinstance(f, np.ufunc):
                    return f(self)
                query_compiler = self.map(f)._query_compiler
        if return_type not in ["DataFrame", "Series"]:
            return query_compiler.to_pandas().squeeze()
        else:
            result = getattr(sys.modules[self.__module__], return_type)(
                query_compiler=query_compiler
            )
            if result.name == self.index[0]:
                result.name = None
            return result