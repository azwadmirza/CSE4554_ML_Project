    def _aggregate(self, arg, *args, **kwargs):
        """
        provide an implementation for the aggregators

        Parameters
        ----------
        arg : string, dict, function
        *args : args to pass on to the function
        **kwargs : kwargs to pass on to the function

        Returns
        -------
        tuple of result, how

        Notes
        -----
        how can be a string describe the required post-processing, or
        None if not required
        """
        is_aggregator = lambda x: isinstance(x, (list, tuple, dict))

        _axis = kwargs.pop("_axis", None)
        if _axis is None:
            _axis = getattr(self, "axis", 0)

        if isinstance(arg, str):
            return self._try_aggregate_string_function(arg, *args, **kwargs), None

        if isinstance(arg, dict):
            # aggregate based on the passed dict
            if _axis != 0:  # pragma: no cover
                raise ValueError("Can only pass dict with axis=0")

            obj = self._selected_obj

            # if we have a dict of any non-scalars
            # eg. {'A' : ['mean']}, normalize all to
            # be list-likes
            if any(is_aggregator(x) for x in arg.values()):
                new_arg = {}
                for k, v in arg.items():
                    if not isinstance(v, (tuple, list, dict)):
                        new_arg[k] = [v]
                    else:
                        new_arg[k] = v

                    # the keys must be in the columns
                    # for ndim=2, or renamers for ndim=1

                    # ok for now, but deprecated
                    # {'A': { 'ra': 'mean' }}
                    # {'A': { 'ra': ['mean'] }}
                    # {'ra': ['mean']}

                    # not ok
                    # {'ra' : { 'A' : 'mean' }}
                    if isinstance(v, dict):
                        raise SpecificationError("nested renamer is not supported")
                    elif isinstance(obj, ABCSeries):
                        raise SpecificationError("nested renamer is not supported")
                    elif isinstance(obj, ABCDataFrame) and k not in obj.columns:
                        raise KeyError(f"Column '{k}' does not exist!")

                arg = new_arg

            else:
                # deprecation of renaming keys
                # GH 15931
                keys = list(arg.keys())
                if isinstance(obj, ABCDataFrame) and len(
                    obj.columns.intersection(keys)
                ) != len(keys):
                    cols = sorted(set(keys) - set(obj.columns.intersection(keys)))
                    raise SpecificationError(f"Column(s) {cols} do not exist")

            from pandas.core.reshape.concat import concat

            def _agg_1dim(name, how, subset=None):
                """
                aggregate a 1-dim with how
                """
                colg = self._gotitem(name, ndim=1, subset=subset)
                if colg.ndim != 1:
                    raise SpecificationError(
                        "nested dictionary is ambiguous in aggregation"
                    )
                return colg.aggregate(how)

            def _agg_2dim(how):
                """
                aggregate a 2-dim with how
                """
                colg = self._gotitem(self._selection, ndim=2, subset=obj)
                return colg.aggregate(how)

            def _agg(arg, func):
                """
                run the aggregations over the arg with func
                return a dict
                """
                result = {}
                for fname, agg_how in arg.items():
                    result[fname] = func(fname, agg_how)
                return result

            # set the final keys
            keys = list(arg.keys())
            result = {}

            if self._selection is not None:

                sl = set(self._selection_list)

                # we are a Series like object,
                # but may have multiple aggregations
                if len(sl) == 1:

                    result = _agg(
                        arg, lambda fname, agg_how: _agg_1dim(self._selection, agg_how)
                    )

                # we are selecting the same set as we are aggregating
                elif not len(sl - set(keys)):

                    result = _agg(arg, _agg_1dim)

                # we are a DataFrame, with possibly multiple aggregations
                else:

                    result = _agg(arg, _agg_2dim)

            # no selection
            else:

                try:
                    result = _agg(arg, _agg_1dim)
                except SpecificationError:

                    # we are aggregating expecting all 1d-returns
                    # but we have 2d
                    result = _agg(arg, _agg_2dim)

            # combine results

            def is_any_series() -> bool:
                # return a boolean if we have *any* nested series
                return any(isinstance(r, ABCSeries) for r in result.values())

            def is_any_frame() -> bool:
                # return a boolean if we have *any* nested series
                return any(isinstance(r, ABCDataFrame) for r in result.values())

            if isinstance(result, list):
                return concat(result, keys=keys, axis=1, sort=True), True

            elif is_any_frame():
                # we have a dict of DataFrames
                # return a MI DataFrame

                keys_to_use = [k for k in keys if not result[k].empty]
                # Have to check, if at least one DataFrame is not empty.
                keys_to_use = keys_to_use if keys_to_use != [] else keys
                return (
                    concat([result[k] for k in keys_to_use], keys=keys_to_use, axis=1),
                    True,
                )

            elif isinstance(self, ABCSeries) and is_any_series():

                # we have a dict of Series
                # return a MI Series
                try:
                    result = concat(result)
                except TypeError as err:
                    # we want to give a nice error here if
                    # we have non-same sized objects, so
                    # we don't automatically broadcast

                    raise ValueError(
                        "cannot perform both aggregation "
                        "and transformation operations "
                        "simultaneously"
                    ) from err

                return result, True

            # fall thru
            from pandas import DataFrame, Series

            try:
                result = DataFrame(result)
            except ValueError:
                # we have a dict of scalars

                # GH 36212 use name only if self is a series
                name = self.name if (self.ndim == 1) else None

                result = Series(result, name=name)

            return result, True
        elif is_list_like(arg):
            # we require a list, but not an 'str'
            return self._aggregate_multiple_funcs(arg, _axis=_axis), None
        else:
            result = None

        f = self._get_cython_func(arg)
        if f and not args and not kwargs:
            return getattr(self, f)(), None

        # caller can react
        return result, True