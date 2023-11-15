    def _aggregate(self, arg, *args, **kwargs):
        _axis = kwargs.pop("_axis", 0)
        kwargs.pop("_level", None)

        if isinstance(arg, str):
            kwargs.pop("is_transform", None)
            return self._string_function(arg, *args, **kwargs)

        # Dictionaries have complex behavior because they can be renamed here.
        elif isinstance(arg, dict):
            return self._default_to_pandas("agg", arg, *args, **kwargs)
        elif is_list_like(arg) or callable(arg):
            kwargs.pop("is_transform", None)
            return self.apply(arg, axis=_axis, args=args, **kwargs)
        else:
            raise TypeError("type {} is not callable".format(type(arg)))