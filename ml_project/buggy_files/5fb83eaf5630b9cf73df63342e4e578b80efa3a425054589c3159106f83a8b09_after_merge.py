    def _wrap_result(self, result, use_codes=True,
                     name=None, expand=None):

        from pandas.core.index import Index, MultiIndex

        # for category, we do the stuff on the categories, so blow it up
        # to the full series again
        # But for some operations, we have to do the stuff on the full values,
        # so make it possible to skip this step as the method already did this
        # before the transformation...
        if use_codes and self._is_categorical:
            result = take_1d(result, self._orig.cat.codes)

        if not hasattr(result, 'ndim') or not hasattr(result, 'dtype'):
            return result
        assert result.ndim < 3

        if expand is None:
            # infer from ndim if expand is not specified
            expand = False if result.ndim == 1 else True

        elif expand is True and not isinstance(self._orig, Index):
            # required when expand=True is explicitly specified
            # not needed when infered

            def cons_row(x):
                if is_list_like(x):
                    return x
                else:
                    return [x]

            result = [cons_row(x) for x in result]

        if not isinstance(expand, bool):
            raise ValueError("expand must be True or False")

        if expand is False:
            # if expand is False, result should have the same name
            # as the original otherwise specified
            if name is None:
                name = getattr(result, 'name', None)
            if name is None:
                # do not use logical or, _orig may be a DataFrame
                # which has "name" column
                name = self._orig.name

        # Wait until we are sure result is a Series or Index before
        # checking attributes (GH 12180)
        if isinstance(self._orig, Index):
            # if result is a boolean np.array, return the np.array
            # instead of wrapping it into a boolean Index (GH 8875)
            if is_bool_dtype(result):
                return result

            if expand:
                result = list(result)
                return MultiIndex.from_tuples(result, names=name)
            else:
                return Index(result, name=name)
        else:
            index = self._orig.index
            if expand:
                cons = self._orig._constructor_expanddim
                return cons(result, index=index)
            else:
                # Must a Series
                cons = self._orig._constructor
                return cons(result, name=name, index=index)