        def __add__(self, other):
            from pandas.core.index import Index
            from pandas.core.indexes.timedeltas import TimedeltaIndex
            from pandas.tseries.offsets import DateOffset
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