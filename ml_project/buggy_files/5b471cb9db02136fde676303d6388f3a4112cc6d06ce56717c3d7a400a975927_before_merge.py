def encode(obj):
    """
    Data encoder
    """
    tobj = type(obj)
    if isinstance(obj, Index):
        if isinstance(obj, RangeIndex):
            return {u'typ': u'range_index',
                    u'klass': u(obj.__class__.__name__),
                    u'name': getattr(obj, 'name', None),
                    u'start': getattr(obj, '_start', None),
                    u'stop': getattr(obj, '_stop', None),
                    u'step': getattr(obj, '_step', None)}
        elif isinstance(obj, PeriodIndex):
            return {u'typ': u'period_index',
                    u'klass': u(obj.__class__.__name__),
                    u'name': getattr(obj, 'name', None),
                    u'freq': u_safe(getattr(obj, 'freqstr', None)),
                    u'dtype': u(obj.dtype.name),
                    u'data': convert(obj.asi8),
                    u'compress': compressor}
        elif isinstance(obj, DatetimeIndex):
            tz = getattr(obj, 'tz', None)

            # store tz info and data as UTC
            if tz is not None:
                tz = u(tz.zone)
                obj = obj.tz_convert('UTC')
            return {u'typ': u'datetime_index',
                    u'klass': u(obj.__class__.__name__),
                    u'name': getattr(obj, 'name', None),
                    u'dtype': u(obj.dtype.name),
                    u'data': convert(obj.asi8),
                    u'freq': u_safe(getattr(obj, 'freqstr', None)),
                    u'tz': tz,
                    u'compress': compressor}
        elif isinstance(obj, MultiIndex):
            return {u'typ': u'multi_index',
                    u'klass': u(obj.__class__.__name__),
                    u'names': getattr(obj, 'names', None),
                    u'dtype': u(obj.dtype.name),
                    u'data': convert(obj.values),
                    u'compress': compressor}
        else:
            return {u'typ': u'index',
                    u'klass': u(obj.__class__.__name__),
                    u'name': getattr(obj, 'name', None),
                    u'dtype': u(obj.dtype.name),
                    u'data': convert(obj.values),
                    u'compress': compressor}

    elif isinstance(obj, Categorical):
        return {u'typ': u'category',
                u'klass': u(obj.__class__.__name__),
                u'name': getattr(obj, 'name', None),
                u'codes': obj.codes,
                u'categories': obj.categories,
                u'ordered': obj.ordered,
                u'compress': compressor}

    elif isinstance(obj, Series):
        if isinstance(obj, SparseSeries):
            raise NotImplementedError(
                'msgpack sparse series is not implemented'
            )
            # d = {'typ': 'sparse_series',
            #     'klass': obj.__class__.__name__,
            #     'dtype': obj.dtype.name,
            #     'index': obj.index,
            #     'sp_index': obj.sp_index,
            #     'sp_values': convert(obj.sp_values),
            #     'compress': compressor}
            # for f in ['name', 'fill_value', 'kind']:
            #    d[f] = getattr(obj, f, None)
            # return d
        else:
            return {u'typ': u'series',
                    u'klass': u(obj.__class__.__name__),
                    u'name': getattr(obj, 'name', None),
                    u'index': obj.index,
                    u'dtype': u(obj.dtype.name),
                    u'data': convert(obj.values),
                    u'compress': compressor}
    elif issubclass(tobj, NDFrame):
        if isinstance(obj, SparseDataFrame):
            raise NotImplementedError(
                'msgpack sparse frame is not implemented'
            )
            # d = {'typ': 'sparse_dataframe',
            #     'klass': obj.__class__.__name__,
            #     'columns': obj.columns}
            # for f in ['default_fill_value', 'default_kind']:
            #    d[f] = getattr(obj, f, None)
            # d['data'] = dict([(name, ss)
            #                 for name, ss in compat.iteritems(obj)])
            # return d
        else:

            data = obj._data
            if not data.is_consolidated():
                data = data.consolidate()

            # the block manager
            return {u'typ': u'block_manager',
                    u'klass': u(obj.__class__.__name__),
                    u'axes': data.axes,
                    u'blocks': [{u'locs': b.mgr_locs.as_array,
                                 u'values': convert(b.values),
                                 u'shape': b.values.shape,
                                 u'dtype': u(b.dtype.name),
                                 u'klass': u(b.__class__.__name__),
                                 u'compress': compressor} for b in data.blocks]
                    }

    elif isinstance(obj, (datetime, date, np.datetime64, timedelta,
                          np.timedelta64)) or obj is NaT:
        if isinstance(obj, Timestamp):
            tz = obj.tzinfo
            if tz is not None:
                tz = u(tz.zone)
            freq = obj.freq
            if freq is not None:
                freq = u(freq.freqstr)
            return {u'typ': u'timestamp',
                    u'value': obj.value,
                    u'freq': freq,
                    u'tz': tz}
        if obj is NaT:
            return {u'typ': u'nat'}
        elif isinstance(obj, np.timedelta64):
            return {u'typ': u'timedelta64',
                    u'data': obj.view('i8')}
        elif isinstance(obj, timedelta):
            return {u'typ': u'timedelta',
                    u'data': (obj.days, obj.seconds, obj.microseconds)}
        elif isinstance(obj, np.datetime64):
            return {u'typ': u'datetime64',
                    u'data': u(str(obj))}
        elif isinstance(obj, datetime):
            return {u'typ': u'datetime',
                    u'data': u(obj.isoformat())}
        elif isinstance(obj, date):
            return {u'typ': u'date',
                    u'data': u(obj.isoformat())}
        raise Exception("cannot encode this datetimelike object: %s" % obj)
    elif isinstance(obj, Period):
        return {u'typ': u'period',
                u'ordinal': obj.ordinal,
                u'freq': u(obj.freq)}
    elif isinstance(obj, BlockIndex):
        return {u'typ': u'block_index',
                u'klass': u(obj.__class__.__name__),
                u'blocs': obj.blocs,
                u'blengths': obj.blengths,
                u'length': obj.length}
    elif isinstance(obj, IntIndex):
        return {u'typ': u'int_index',
                u'klass': u(obj.__class__.__name__),
                u'indices': obj.indices,
                u'length': obj.length}
    elif isinstance(obj, np.ndarray):
        return {u'typ': u'ndarray',
                u'shape': obj.shape,
                u'ndim': obj.ndim,
                u'dtype': u(obj.dtype.name),
                u'data': convert(obj),
                u'compress': compressor}
    elif isinstance(obj, np.number):
        if np.iscomplexobj(obj):
            return {u'typ': u'np_scalar',
                    u'sub_typ': u'np_complex',
                    u'dtype': u(obj.dtype.name),
                    u'real': u(obj.real.__repr__()),
                    u'imag': u(obj.imag.__repr__())}
        else:
            return {u'typ': u'np_scalar',
                    u'dtype': u(obj.dtype.name),
                    u'data': u(obj.__repr__())}
    elif isinstance(obj, complex):
        return {u'typ': u'np_complex',
                u'real': u(obj.real.__repr__()),
                u'imag': u(obj.imag.__repr__())}

    return obj