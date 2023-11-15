    def _wrap_result(self, result, use_codes=True, name=None):

        # for category, we do the stuff on the categories, so blow it up
        # to the full series again
        # But for some operations, we have to do the stuff on the full values,
        # so make it possible to skip this step as the method already did this
        # before the transformation...
        if use_codes and self._is_categorical:
            result = take_1d(result, self._orig.cat.codes)

        # leave as it is to keep extract and get_dummies results
        # can be merged to _wrap_result_expand in v0.17
        from pandas.core.series import Series
        from pandas.core.frame import DataFrame
        from pandas.core.index import Index

        if not hasattr(result, 'ndim'):
            return result
        name = name or getattr(result, 'name', None) or self._orig.name

        if result.ndim == 1:
            if isinstance(self._orig, Index):
                # if result is a boolean np.array, return the np.array
                # instead of wrapping it into a boolean Index (GH 8875)
                if is_bool_dtype(result):
                    return result
                return Index(result, name=name)
            return Series(result, index=self._orig.index, name=name)
        else:
            assert result.ndim < 3
            return DataFrame(result, index=self._orig.index)