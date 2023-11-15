    def _add_datetimelike_methods(cls):
        """
        add in the datetimelike methods (as we may have to override the
        superclass)
        """

        def __add__(self, other):
            from pandas.core.index import Index
            from pandas.core.indexes.timedeltas import TimedeltaIndex
            from pandas.tseries.offsets import DateOffset

            other = lib.item_from_zerodim(other)
            if is_timedelta64_dtype(other):
                return self._add_delta(other)
            elif isinstance(self, TimedeltaIndex) and isinstance(other, Index):
                if hasattr(other, '_add_delta'):
                    return other._add_delta(self)
                raise TypeError("cannot add TimedeltaIndex and {typ}"
                                .format(typ=type(other)))
            elif isinstance(other, (DateOffset, timedelta)):
                return self._add_delta(other)
            elif is_integer(other):
                return self.shift(other)
            elif isinstance(other, (datetime, np.datetime64)):
                return self._add_datelike(other)
            elif is_offsetlike(other):
                # Array/Index of DateOffset objects
                return self._add_offset_array(other)
            elif isinstance(other, Index):
                return self._add_datelike(other)
            else:  # pragma: no cover
                return NotImplemented

        cls.__add__ = __add__
        cls.__radd__ = __add__

        def __sub__(self, other):
            from pandas.core.index import Index
            from pandas.core.indexes.datetimes import DatetimeIndex
            from pandas.core.indexes.timedeltas import TimedeltaIndex
            from pandas.tseries.offsets import DateOffset

            other = lib.item_from_zerodim(other)
            if is_timedelta64_dtype(other):
                return self._add_delta(-other)
            elif isinstance(self, TimedeltaIndex) and isinstance(other, Index):
                if not isinstance(other, TimedeltaIndex):
                    raise TypeError("cannot subtract TimedeltaIndex and {typ}"
                                    .format(typ=type(other).__name__))
                return self._add_delta(-other)
            elif isinstance(other, DatetimeIndex):
                return self._sub_datelike(other)
            elif isinstance(other, (DateOffset, timedelta)):
                return self._add_delta(-other)
            elif is_integer(other):
                return self.shift(-other)
            elif isinstance(other, (datetime, np.datetime64)):
                return self._sub_datelike(other)
            elif isinstance(other, Period):
                return self._sub_period(other)
            elif is_offsetlike(other):
                # Array/Index of DateOffset objects
                return self._sub_offset_array(other)
            elif isinstance(other, Index):
                raise TypeError("cannot subtract {typ1} and {typ2}"
                                .format(typ1=type(self).__name__,
                                        typ2=type(other).__name__))

            else:  # pragma: no cover
                return NotImplemented

        cls.__sub__ = __sub__

        def __rsub__(self, other):
            return -(self - other)
        cls.__rsub__ = __rsub__

        cls.__iadd__ = __add__
        cls.__isub__ = __sub__