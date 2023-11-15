    def apply(self, func, axis=0, raw=False, result_type=None, args=(), **kwds):
        axis = self._get_axis_number(axis)
        query_compiler = super(DataFrame, self).apply(
            func, axis=axis, raw=raw, result_type=result_type, args=args, **kwds
        )
        if not isinstance(query_compiler, type(self._query_compiler)):
            return query_compiler
        # This is the simplest way to determine the return type, but there are checks
        # in pandas that verify that some results are created. This is a challenge for
        # empty DataFrames, but fortunately they only happen when the `func` type is
        # a list or a dictionary, which means that the return type won't change from
        # type(self), so we catch that error and use `self.__name__` for the return
        # type.
        try:
            if axis == 0:
                init_kwargs = {"index": self.index}
            else:
                init_kwargs = {"columns": self.columns}
            return_type = type(
                getattr(pandas, self.__name__)(**init_kwargs).apply(
                    func, axis=axis, raw=raw, result_type=result_type,
                )
            ).__name__
        except Exception:
            return_type = self.__name__
        if return_type not in ["DataFrame", "Series"]:
            return query_compiler.to_pandas().squeeze()
        else:
            result = getattr(sys.modules[self.__module__], return_type)(
                query_compiler=query_compiler
            )
            if hasattr(result, "name"):
                if axis == 0 and result.name == self.index[0]:
                    result.name = None
                elif axis == 1 and result.name == self.columns[0]:
                    result.name = None
            return result