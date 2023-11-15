    def aggregate(self, func=None, *args, **kwargs):
        if self._axis != 0:
            # This is not implemented in pandas,
            # so we throw a different message
            raise NotImplementedError("axis other than 0 is not supported")

        if (
            callable(func)
            and isinstance(func, BuiltinFunctionType)
            and func.__name__ in dir(self)
        ):
            func = func.__name__

        relabeling_required = False
        if isinstance(func, dict) or func is None:

            def _reconstruct_func(func, **kwargs):
                relabeling_required, func, new_columns, order = reconstruct_func(
                    func, **kwargs
                )
                # We convert to the string version of the function for simplicity.
                func = {
                    k: v
                    if not callable(v) or v.__name__ not in dir(self)
                    else v.__name__
                    for k, v in func.items()
                }
                return relabeling_required, func, new_columns, order

            relabeling_required, func_dict, new_columns, order = _reconstruct_func(
                func, **kwargs
            )

            if any(i not in self._df.columns for i in func_dict.keys()):
                from pandas.core.base import SpecificationError

                raise SpecificationError("nested renamer is not supported")
            func = func_dict
        elif is_list_like(func):
            return self._default_to_pandas(
                lambda df, *args, **kwargs: df.aggregate(func, *args, **kwargs),
                *args,
                **kwargs,
            )
        elif callable(func):
            return self._apply_agg_function(
                lambda grp, *args, **kwargs: grp.aggregate(func, *args, **kwargs),
                *args,
                **kwargs,
            )
        elif isinstance(func, str):
            # Using "getattr" here masks possible AttributeError which we throw
            # in __getattr__, so we should call __getattr__ directly instead.
            agg_func = self.__getattr__(func)
            if callable(agg_func):
                return agg_func(*args, **kwargs)

        result = self._apply_agg_function(
            func,
            *args,
            **kwargs,
        )

        if relabeling_required:
            result = result.iloc[:, order]
            result.columns = new_columns
        return result