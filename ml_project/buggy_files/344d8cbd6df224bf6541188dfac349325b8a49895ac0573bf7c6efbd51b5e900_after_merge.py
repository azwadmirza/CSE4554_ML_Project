    def _parsed_string_to_bounds(self, reso: Resolution, parsed: datetime):
        """
        Calculate datetime bounds for parsed time string and its resolution.

        Parameters
        ----------
        reso : str
            Resolution provided by parsed string.
        parsed : datetime
            Datetime from parsed string.

        Returns
        -------
        lower, upper: pd.Timestamp
        """
        assert isinstance(reso, Resolution), (type(reso), reso)
        valid_resos = {
            "year",
            "month",
            "quarter",
            "day",
            "hour",
            "minute",
            "second",
            "minute",
            "second",
            "millisecond",
            "microsecond",
        }
        if reso.attrname not in valid_resos:
            raise KeyError

        grp = reso.freq_group
        per = Period(parsed, freq=grp.value)
        start, end = per.start_time, per.end_time

        # GH 24076
        # If an incoming date string contained a UTC offset, need to localize
        # the parsed date to this offset first before aligning with the index's
        # timezone
        if parsed.tzinfo is not None:
            if self.tz is None:
                raise ValueError(
                    "The index must be timezone aware when indexing "
                    "with a date string with a UTC offset"
                )
            start = start.tz_localize(parsed.tzinfo).tz_convert(self.tz)
            end = end.tz_localize(parsed.tzinfo).tz_convert(self.tz)
        elif self.tz is not None:
            start = start.tz_localize(self.tz)
            end = end.tz_localize(self.tz)
        return start, end