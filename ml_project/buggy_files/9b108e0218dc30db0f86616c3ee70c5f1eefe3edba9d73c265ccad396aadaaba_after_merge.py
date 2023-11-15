    def _add_datelike(self, other):
        # adding a timedeltaindex to a datetimelike
        from pandas import Timestamp, DatetimeIndex
        if other is NaT:
            result = self._nat_new(box=False)
        else:
            other = Timestamp(other)
            i8 = self.asi8
            result = checked_add_with_arr(i8, other.value,
                                          arr_mask=self._isnan)
            result = self._maybe_mask_results(result, fill_value=iNaT)
        return DatetimeIndex(result, name=self.name, copy=False)