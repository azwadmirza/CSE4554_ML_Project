    def _apply_standard(self, func, axis, ignore_failures=False, reduce=True):

        # skip if we are mixed datelike and trying reduce across axes
        # GH6125
        if (reduce and axis == 1 and self._is_mixed_type and
                self._is_datelike_mixed_type):
            reduce = False

        # try to reduce first (by default)
        # this only matters if the reduction in values is of different dtype
        # e.g. if we want to apply to a SparseFrame, then can't directly reduce
        if reduce:
            values = self.values

            # we cannot reduce using non-numpy dtypes,
            # as demonstrated in gh-12244
            if not is_extension_type(values):
                # Create a dummy Series from an empty array
                index = self._get_axis(axis)
                empty_arr = np.empty(len(index), dtype=values.dtype)
                dummy = Series(empty_arr, index=self._get_axis(axis),
                               dtype=values.dtype)

                try:
                    labels = self._get_agg_axis(axis)
                    result = lib.reduce(values, func, axis=axis, dummy=dummy,
                                        labels=labels)
                    return Series(result, index=labels)
                except Exception:
                    pass

        dtype = object if self._is_mixed_type else None
        if axis == 0:
            series_gen = (self._ixs(i, axis=1)
                          for i in range(len(self.columns)))
            res_index = self.columns
            res_columns = self.index
        elif axis == 1:
            res_index = self.index
            res_columns = self.columns
            values = self.values
            series_gen = (Series.from_array(arr, index=res_columns, name=name,
                                            dtype=dtype)
                          for i, (arr, name) in enumerate(zip(values,
                                                              res_index)))
        else:  # pragma : no cover
            raise AssertionError('Axis must be 0 or 1, got %s' % str(axis))

        i = None
        keys = []
        results = {}
        if ignore_failures:
            successes = []
            for i, v in enumerate(series_gen):
                try:
                    results[i] = func(v)
                    keys.append(v.name)
                    successes.append(i)
                except Exception:
                    pass
            # so will work with MultiIndex
            if len(successes) < len(res_index):
                res_index = res_index.take(successes)
        else:
            try:
                for i, v in enumerate(series_gen):
                    results[i] = func(v)
                    keys.append(v.name)
            except Exception as e:
                if hasattr(e, 'args'):
                    # make sure i is defined
                    if i is not None:
                        k = res_index[i]
                        e.args = e.args + ('occurred at index %s' %
                                           pprint_thing(k), )
                raise

        if len(results) > 0 and is_sequence(results[0]):
            if not isinstance(results[0], Series):
                index = res_columns
            else:
                index = None

            result = self._constructor(data=results, index=index)
            result.columns = res_index

            if axis == 1:
                result = result.T
            result = result._convert(datetime=True, timedelta=True, copy=False)

        else:

            result = Series(results)
            result.index = res_index

        return result