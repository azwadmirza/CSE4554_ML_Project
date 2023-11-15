def decode(obj):
    """
    Decoder for deserializing numpy data types.
    """

    typ = obj.get(u'typ')
    if typ is None:
        return obj
    elif typ == u'timestamp':
        freq = obj[u'freq'] if 'freq' in obj else obj[u'offset']
        return Timestamp(obj[u'value'], tz=obj[u'tz'], freq=freq)
    elif typ == u'nat':
        return NaT
    elif typ == u'period':
        return Period(ordinal=obj[u'ordinal'], freq=obj[u'freq'])
    elif typ == u'index':
        dtype = dtype_for(obj[u'dtype'])
        data = unconvert(obj[u'data'], dtype,
                         obj.get(u'compress'))
        return globals()[obj[u'klass']](data, dtype=dtype, name=obj[u'name'])
    elif typ == u'range_index':
        return globals()[obj[u'klass']](obj[u'start'],
                                        obj[u'stop'],
                                        obj[u'step'],
                                        name=obj[u'name'])
    elif typ == u'multi_index':
        dtype = dtype_for(obj[u'dtype'])
        data = unconvert(obj[u'data'], dtype,
                         obj.get(u'compress'))
        data = [tuple(x) for x in data]
        return globals()[obj[u'klass']].from_tuples(data, names=obj[u'names'])
    elif typ == u'period_index':
        data = unconvert(obj[u'data'], np.int64, obj.get(u'compress'))
        d = dict(name=obj[u'name'], freq=obj[u'freq'])
        freq = d.pop('freq', None)
        return globals()[obj[u'klass']](PeriodArray(data, freq), **d)

    elif typ == u'datetime_index':
        data = unconvert(obj[u'data'], np.int64, obj.get(u'compress'))
        d = dict(name=obj[u'name'], freq=obj[u'freq'])
        result = DatetimeIndex._simple_new(data, **d)
        tz = obj[u'tz']

        # reverse tz conversion
        if tz is not None:
            result = result.tz_localize('UTC').tz_convert(tz)
        return result

    elif typ in (u'interval_index', 'interval_array'):
        return globals()[obj[u'klass']].from_arrays(obj[u'left'],
                                                    obj[u'right'],
                                                    obj[u'closed'],
                                                    name=obj[u'name'])
    elif typ == u'category':
        from_codes = globals()[obj[u'klass']].from_codes
        return from_codes(codes=obj[u'codes'],
                          categories=obj[u'categories'],
                          ordered=obj[u'ordered'])

    elif typ == u'interval':
        return Interval(obj[u'left'], obj[u'right'], obj[u'closed'])
    elif typ == u'series':
        dtype = dtype_for(obj[u'dtype'])
        pd_dtype = pandas_dtype(dtype)

        index = obj[u'index']
        result = globals()[obj[u'klass']](unconvert(obj[u'data'], dtype,
                                                    obj[u'compress']),
                                          index=index,
                                          dtype=pd_dtype,
                                          name=obj[u'name'])
        return result

    elif typ == u'block_manager':
        axes = obj[u'axes']

        def create_block(b):
            values = _safe_reshape(unconvert(
                b[u'values'], dtype_for(b[u'dtype']),
                b[u'compress']), b[u'shape'])

            # locs handles duplicate column names, and should be used instead
            # of items; see GH 9618
            if u'locs' in b:
                placement = b[u'locs']
            else:
                placement = axes[0].get_indexer(b[u'items'])
            return make_block(values=values,
                              klass=getattr(internals, b[u'klass']),
                              placement=placement,
                              dtype=b[u'dtype'])

        blocks = [create_block(b) for b in obj[u'blocks']]
        return globals()[obj[u'klass']](BlockManager(blocks, axes))
    elif typ == u'datetime':
        return parse(obj[u'data'])
    elif typ == u'datetime64':
        return np.datetime64(parse(obj[u'data']))
    elif typ == u'date':
        return parse(obj[u'data']).date()
    elif typ == u'timedelta':
        return timedelta(*obj[u'data'])
    elif typ == u'timedelta64':
        return np.timedelta64(int(obj[u'data']))
    # elif typ == 'sparse_series':
    #    dtype = dtype_for(obj['dtype'])
    #    return globals()[obj['klass']](
    #        unconvert(obj['sp_values'], dtype, obj['compress']),
    #        sparse_index=obj['sp_index'], index=obj['index'],
    #        fill_value=obj['fill_value'], kind=obj['kind'], name=obj['name'])
    # elif typ == 'sparse_dataframe':
    #    return globals()[obj['klass']](
    #        obj['data'], columns=obj['columns'],
    #        default_fill_value=obj['default_fill_value'],
    #        default_kind=obj['default_kind']
    #    )
    # elif typ == 'sparse_panel':
    #    return globals()[obj['klass']](
    #        obj['data'], items=obj['items'],
    #        default_fill_value=obj['default_fill_value'],
    #        default_kind=obj['default_kind'])
    elif typ == u'block_index':
        return globals()[obj[u'klass']](obj[u'length'], obj[u'blocs'],
                                        obj[u'blengths'])
    elif typ == u'int_index':
        return globals()[obj[u'klass']](obj[u'length'], obj[u'indices'])
    elif typ == u'ndarray':
        return unconvert(obj[u'data'], np.typeDict[obj[u'dtype']],
                         obj.get(u'compress')).reshape(obj[u'shape'])
    elif typ == u'np_scalar':
        if obj.get(u'sub_typ') == u'np_complex':
            return c2f(obj[u'real'], obj[u'imag'], obj[u'dtype'])
        else:
            dtype = dtype_for(obj[u'dtype'])
            try:
                return dtype(obj[u'data'])
            except (ValueError, TypeError):
                return dtype.type(obj[u'data'])
    elif typ == u'np_complex':
        return complex(obj[u'real'] + u'+' + obj[u'imag'] + u'j')
    elif isinstance(obj, (dict, list, set)):
        return obj
    else:
        return obj