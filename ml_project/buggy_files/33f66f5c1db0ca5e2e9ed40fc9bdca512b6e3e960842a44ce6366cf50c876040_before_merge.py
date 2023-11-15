    def _convert_to_array(self, values, name=None, other=None):
        """converts values to ndarray"""
        from pandas.tseries.timedeltas import to_timedelta

        ovalues = values
        supplied_dtype = None
        if not is_list_like(values):
            values = np.array([values])
        # if this is a Series that contains relevant dtype info, then use this
        # instead of the inferred type; this avoids coercing Series([NaT],
        # dtype='datetime64[ns]') to Series([NaT], dtype='timedelta64[ns]')
        elif (isinstance(values, pd.Series) and
              (is_timedelta64_dtype(values) or is_datetime64_dtype(values))):
            supplied_dtype = values.dtype
        inferred_type = supplied_dtype or lib.infer_dtype(values)
        if (inferred_type in ('datetime64', 'datetime', 'date', 'time') or
                is_datetimetz(inferred_type)):
            # if we have a other of timedelta, but use pd.NaT here we
            # we are in the wrong path
            if (supplied_dtype is None and other is not None and
                (other.dtype in ('timedelta64[ns]', 'datetime64[ns]')) and
                    isnull(values).all()):
                values = np.empty(values.shape, dtype='timedelta64[ns]')
                values[:] = iNaT

            # a datelike
            elif isinstance(values, pd.DatetimeIndex):
                values = values.to_series()
            # datetime with tz
            elif (isinstance(ovalues, datetime.datetime) and
                  hasattr(ovalues, 'tz')):
                values = pd.DatetimeIndex(values)
            # datetime array with tz
            elif is_datetimetz(values):
                if isinstance(values, ABCSeries):
                    values = values._values
            elif not (isinstance(values, (np.ndarray, ABCSeries)) and
                      is_datetime64_dtype(values)):
                values = tslib.array_to_datetime(values)
        elif inferred_type in ('timedelta', 'timedelta64'):
            # have a timedelta, convert to to ns here
            values = to_timedelta(values, errors='coerce', box=False)
        elif inferred_type == 'integer':
            # py3 compat where dtype is 'm' but is an integer
            if values.dtype.kind == 'm':
                values = values.astype('timedelta64[ns]')
            elif isinstance(values, pd.PeriodIndex):
                values = values.to_timestamp().to_series()
            elif name not in ('__truediv__', '__div__', '__mul__', '__rmul__'):
                raise TypeError("incompatible type for a datetime/timedelta "
                                "operation [{0}]".format(name))
        elif inferred_type == 'floating':
            if (isnull(values).all() and
                    name in ('__add__', '__radd__', '__sub__', '__rsub__')):
                values = np.empty(values.shape, dtype=other.dtype)
                values[:] = iNaT
            return values
        elif self._is_offset(values):
            return values
        else:
            raise TypeError("incompatible type [{0}] for a datetime/timedelta"
                            " operation".format(np.array(values).dtype))

        return values