    def get_loc(self, key, method=None, tolerance=None):
        """
        Get integer location for requested label.

        Parameters
        ----------
        key : Period, NaT, str, or datetime
            String or datetime key must be parsable as Period.

        Returns
        -------
        loc : int or ndarray[int64]

        Raises
        ------
        KeyError
            Key is not present in the index.
        TypeError
            If key is listlike or otherwise not hashable.
        """
        orig_key = key

        if not is_scalar(key):
            raise InvalidIndexError(key)

        if isinstance(key, str):

            try:
                loc = self._get_string_slice(key)
                return loc
            except (TypeError, ValueError):
                pass

            try:
                asdt, reso = parse_time_string(key, self.freq)
            except DateParseError as err:
                # A string with invalid format
                raise KeyError(f"Cannot interpret '{key}' as period") from err

            reso = Resolution.from_attrname(reso)
            grp = reso.freq_group
            freqn = self.dtype.freq_group

            # _get_string_slice will handle cases where grp < freqn
            assert grp >= freqn

            # BusinessDay is a bit strange. It has a *lower* code, but we never parse
            # a string as "BusinessDay" resolution, just Day.
            if grp == freqn or (
                reso == Resolution.RESO_DAY and self.dtype.freq.name == "B"
            ):
                key = Period(asdt, freq=self.freq)
                loc = self.get_loc(key, method=method, tolerance=tolerance)
                return loc
            elif method is None:
                raise KeyError(key)
            else:
                key = asdt

        elif is_integer(key):
            # Period constructor will cast to string, which we dont want
            raise KeyError(key)

        try:
            key = Period(key, freq=self.freq)
        except ValueError as err:
            # we cannot construct the Period
            raise KeyError(orig_key) from err

        try:
            return Index.get_loc(self, key, method, tolerance)
        except KeyError as err:
            raise KeyError(orig_key) from err