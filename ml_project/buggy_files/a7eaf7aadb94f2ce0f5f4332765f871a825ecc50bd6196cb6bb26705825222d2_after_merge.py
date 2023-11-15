    def _aggregate(self, func, *args, **kwargs):
        _axis = kwargs.pop("_axis", 0)
        kwargs.pop("_level", None)

        if isinstance(func, str):
            kwargs.pop("is_transform", None)
            return self._string_function(func, *args, **kwargs)

        # Dictionaries have complex behavior because they can be renamed here.
        elif func is None or isinstance(func, dict):
            return self._default_to_pandas("agg", func, *args, **kwargs)
        elif is_list_like(func) or callable(func):
            kwargs.pop("is_transform", None)
            return self.apply(func, axis=_axis, args=args, **kwargs)
        else:
            raise TypeError("type {} is not callable".format(type(func)))