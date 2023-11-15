    def _generate(cls, start, end, periods, name, offset,
                  tz=None, normalize=False, ambiguous='raise', closed=None):
        if com._count_not_none(start, end, periods) != 2:
            raise ValueError('Must specify two of start, end, or periods')

        _normalized = True

        if start is not None:
            start = Timestamp(start)

        if end is not None:
            end = Timestamp(end)

        left_closed = False
        right_closed = False

        if start is None and end is None:
            if closed is not None:
                raise ValueError("Closed has to be None if not both of start"
                                 "and end are defined")

        if closed is None:
            left_closed = True
            right_closed = True
        elif closed == "left":
            left_closed = True
        elif closed == "right":
            right_closed = True
        else:
            raise ValueError("Closed has to be either 'left', 'right' or None")

        try:
            inferred_tz = tools._infer_tzinfo(start, end)
        except:
            raise TypeError('Start and end cannot both be tz-aware with '
                            'different timezones')

        inferred_tz = tslib.maybe_get_tz(inferred_tz)

        # these may need to be localized
        tz = tslib.maybe_get_tz(tz)
        if tz is not None:
            date = start or end
            if date.tzinfo is not None and hasattr(tz, 'localize'):
                tz = tz.localize(date.replace(tzinfo=None)).tzinfo

        if tz is not None and inferred_tz is not None:
            if not inferred_tz == tz:
                raise AssertionError("Inferred time zone not equal to passed "
                                     "time zone")

        elif inferred_tz is not None:
            tz = inferred_tz

        if start is not None:
            if normalize:
                start = normalize_date(start)
                _normalized = True
            else:
                _normalized = _normalized and start.time() == _midnight

        if end is not None:
            if normalize:
                end = normalize_date(end)
                _normalized = True
            else:
                _normalized = _normalized and end.time() == _midnight

        if hasattr(offset, 'delta') and offset != offsets.Day():
            if inferred_tz is None and tz is not None:
                # naive dates
                if start is not None and start.tz is None:
                    start = start.tz_localize(tz, ambiguous=False)

                if end is not None and end.tz is None:
                    end = end.tz_localize(tz, ambiguous=False)

            if start and end:
                if start.tz is None and end.tz is not None:
                    start = start.tz_localize(end.tz, ambiguous=False)

                if end.tz is None and start.tz is not None:
                    end = end.tz_localize(start.tz, ambiguous=False)

            if _use_cached_range(offset, _normalized, start, end):
                index = cls._cached_range(start, end, periods=periods,
                                          offset=offset, name=name)
            else:
                index = _generate_regular_range(start, end, periods, offset)

        else:

            if tz is not None:
                # naive dates
                if start is not None and start.tz is not None:
                    start = start.replace(tzinfo=None)

                if end is not None and end.tz is not None:
                    end = end.replace(tzinfo=None)

            if start and end:
                if start.tz is None and end.tz is not None:
                    end = end.replace(tzinfo=None)

                if end.tz is None and start.tz is not None:
                    start = start.replace(tzinfo=None)

            if _use_cached_range(offset, _normalized, start, end):
                index = cls._cached_range(start, end, periods=periods,
                                          offset=offset, name=name)
            else:
                index = _generate_regular_range(start, end, periods, offset)

            if tz is not None and getattr(index, 'tz', None) is None:
                index = tslib.tz_localize_to_utc(_ensure_int64(index), tz,
                                                 ambiguous=ambiguous)
                index = index.view(_NS_DTYPE)

                # index is localized datetime64 array -> have to convert
                # start/end as well to compare
                if start is not None:
                    start = start.tz_localize(tz).asm8
                if end is not None:
                    end = end.tz_localize(tz).asm8

        if not left_closed and len(index) and index[0] == start:
            index = index[1:]
        if not right_closed and len(index) and index[-1] == end:
            index = index[:-1]
        index = cls._simple_new(index, name=name, freq=offset, tz=tz)
        return index