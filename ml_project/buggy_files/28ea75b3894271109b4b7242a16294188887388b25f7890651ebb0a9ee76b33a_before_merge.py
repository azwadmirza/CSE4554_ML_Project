    def _generate(cls, start, end, periods, name, offset,
                  tz=None, normalize=False):
        if com._count_not_none(start, end, periods) < 2:
            raise ValueError('Must specify two of start, end, or periods')

        _normalized = True

        if start is not None:
            start = Timestamp(start)

        if end is not None:
            end = Timestamp(end)

        inferred_tz = tools._infer_tzinfo(start, end)

        if tz is not None and inferred_tz is not None:
            assert(inferred_tz == tz)
        elif inferred_tz is not None:
            tz = inferred_tz

        tz = tools._maybe_get_tz(tz)

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

        if hasattr(offset, 'delta'):
            if inferred_tz is None and tz is not None:
                # naive dates
                if start is not None and start.tz is None:
                    start = start.tz_localize(tz)

                if end is not None and end.tz is None:
                    end = end.tz_localize(tz)

            if start and end:
                if start.tz is None and end.tz is not None:
                    start = start.tz_localize(end.tz)

                if end.tz is None and start.tz is not None:
                    end = end.tz_localize(start.tz)


            if (offset._should_cache() and
                not (offset._normalize_cache and not _normalized) and
                _naive_in_cache_range(start, end)):
                index = cls._cached_range(start, end, periods=periods,
                                          offset=offset, name=name)
            else:
                index = _generate_regular_range(start, end, periods, offset)

        else:

            if inferred_tz is None and tz is not None:
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

            if (offset._should_cache() and
                not (offset._normalize_cache and not _normalized) and
                _naive_in_cache_range(start, end)):
                index = cls._cached_range(start, end, periods=periods,
                                          offset=offset, name=name)
            else:
                index = _generate_regular_range(start, end, periods, offset)

            if tz is not None and getattr(index, 'tz', None) is None:
                index = lib.tz_localize_to_utc(com._ensure_int64(index), tz)
                index = index.view(_NS_DTYPE)

        index = index.view(cls)
        index.name = name
        index.offset = offset
        index.tz = tz

        return index