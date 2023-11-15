    def _add_datelike(self, other):

        # adding a timedeltaindex to a datetimelike
        from pandas import Timestamp, DatetimeIndex
        other = Timestamp(other)
        i8 = self.asi8
        result = i8 + other.value
        result = self._maybe_mask_results(result, fill_value=tslib.iNaT)
        return DatetimeIndex(result, name=self.name, copy=False)