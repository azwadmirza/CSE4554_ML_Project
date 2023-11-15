    def _astype(self, dtype, copy=False, errors='raise', values=None,
                klass=None, mgr=None, **kwargs):
        """
        Coerce to the new type (if copy=True, return a new copy)
        raise on an except if raise == True
        """
        errors_legal_values = ('raise', 'ignore')

        if errors not in errors_legal_values:
            invalid_arg = ("Expected value of kwarg 'errors' to be one of {}. "
                           "Supplied value is '{}'".format(
                               list(errors_legal_values), errors))
            raise ValueError(invalid_arg)

        # may need to convert to categorical
        # this is only called for non-categoricals
        if self.is_categorical_astype(dtype):
            return self.make_block(Categorical(self.values, **kwargs))

        # astype processing
        dtype = np.dtype(dtype)
        if self.dtype == dtype:
            if copy:
                return self.copy()
            return self

        if klass is None:
            if dtype == np.object_:
                klass = ObjectBlock
        try:
            # force the copy here
            if values is None:

                if issubclass(dtype.type,
                              (compat.text_type, compat.string_types)):

                    # use native type formatting for datetime/tz/timedelta
                    if self.is_datelike:
                        values = self.to_native_types()

                    # astype formatting
                    else:
                        values = self.values

                else:
                    values = self.get_values(dtype=dtype)

                # _astype_nansafe works fine with 1-d only
                values = astype_nansafe(values.ravel(), dtype, copy=True)
                values = values.reshape(self.shape)

            newb = make_block(values, placement=self.mgr_locs, dtype=dtype,
                              klass=klass)
        except:
            if errors == 'raise':
                raise
            newb = self.copy() if copy else self

        if newb.is_numeric and self.is_numeric:
            if newb.shape != self.shape:
                raise TypeError("cannot set astype for copy = [%s] for dtype "
                                "(%s [%s]) with smaller itemsize that current "
                                "(%s [%s])" % (copy, self.dtype.name,
                                               self.itemsize, newb.dtype.name,
                                               newb.itemsize))
        return newb