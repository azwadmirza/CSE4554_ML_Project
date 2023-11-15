    def _ewma(v):
        result = _tseries.ewma(v, com)
        first_index = _first_valid_index(v)
        result[first_index : first_index + min_periods] = NaN
        return result