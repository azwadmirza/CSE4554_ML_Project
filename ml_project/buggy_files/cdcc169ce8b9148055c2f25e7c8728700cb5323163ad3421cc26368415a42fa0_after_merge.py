    def _ewma(v):
        result = lib.ewma(v, com, int(adjust))
        first_index = _first_valid_index(v)
        result[first_index : first_index + min_periods] = NaN
        return result