    def __new__(cls, start=None, end=None, periods=None,
                offset=datetools.bday, time_rule=None,
                tzinfo=None, name=None, **kwds):

        time_rule = kwds.get('timeRule', time_rule)
        if time_rule is not None:
            offset = datetools.getOffset(time_rule)

        if time_rule is None:
            if offset in datetools._offsetNames:
                time_rule = datetools._offsetNames[offset]

        # Cachable
        if not start:
            start = kwds.get('begin')
        if not periods:
            periods = kwds.get('nPeriods')

        start = datetools.to_datetime(start)
        end = datetools.to_datetime(end)

        if start is not None and not isinstance(start, datetime):
            raise ValueError('Failed to convert %s to datetime' % start)

        if end is not None and not isinstance(end, datetime):
            raise ValueError('Failed to convert %s to datetime' % end)

        # inside cache range. Handle UTC case
        useCache = _will_use_cache(offset)

        start, end, tzinfo = _figure_out_timezone(start, end, tzinfo)
        useCache = useCache and _naive_in_cache_range(start, end)

        if useCache:
            index = cls._cached_range(start, end, periods=periods,
                                      offset=offset, time_rule=time_rule,
                                      name=name)
            if tzinfo is None:
                return index
        else:
            xdr = generate_range(start=start, end=end, periods=periods,
                                 offset=offset, time_rule=time_rule)
            index = list(xdr)

        if tzinfo is not None:
            index = [d.replace(tzinfo=tzinfo) for d in index]

        index = np.array(index, dtype=object, copy=False)
        index = index.view(cls)
        index.name = name
        index.offset = offset
        index.tzinfo = tzinfo
        return index