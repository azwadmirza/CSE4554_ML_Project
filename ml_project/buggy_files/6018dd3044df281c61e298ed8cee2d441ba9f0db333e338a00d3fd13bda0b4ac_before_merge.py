    def __floordiv__(self, other):

        if is_scalar(other):
            if isinstance(other, (timedelta, np.timedelta64, Tick)):
                other = Timedelta(other)
                if other is NaT:
                    # treat this specifically as timedelta-NaT
                    result = np.empty(self.shape, dtype=np.float64)
                    result.fill(np.nan)
                    return result

                # dispatch to Timedelta implementation
                result = other.__rfloordiv__(self._data)
                return result

            # at this point we should only have numeric scalars; anything
            #  else will raise
            result = self.asi8 // other
            result[self._isnan] = iNaT
            freq = None
            if self.freq is not None:
                # Note: freq gets division, not floor-division
                freq = self.freq / other
                if freq.nanos == 0 and self.freq.nanos != 0:
                    # e.g. if self.freq is Nano(1) then dividing by 2
                    #  rounds down to zero
                    freq = None
            return type(self)(result.view("m8[ns]"), freq=freq)

        if not hasattr(other, "dtype"):
            # list, tuple
            other = np.array(other)
        if len(other) != len(self):
            raise ValueError("Cannot divide with unequal lengths")

        elif is_timedelta64_dtype(other.dtype):
            other = type(self)(other)

            # numpy timedelta64 does not natively support floordiv, so operate
            #  on the i8 values
            result = self.asi8 // other.asi8
            mask = self._isnan | other._isnan
            if mask.any():
                result = result.astype(np.int64)
                result[mask] = np.nan
            return result

        elif is_object_dtype(other.dtype):
            result = [self[n] // other[n] for n in range(len(self))]
            result = np.array(result)
            if lib.infer_dtype(result, skipna=False) == "timedelta":
                result, _ = sequence_to_td64ns(result)
                return type(self)(result)
            return result

        elif is_integer_dtype(other.dtype) or is_float_dtype(other.dtype):
            result = self._data // other
            return type(self)(result)

        else:
            dtype = getattr(other, "dtype", type(other).__name__)
            raise TypeError(f"Cannot divide {dtype} by {type(self).__name__}")