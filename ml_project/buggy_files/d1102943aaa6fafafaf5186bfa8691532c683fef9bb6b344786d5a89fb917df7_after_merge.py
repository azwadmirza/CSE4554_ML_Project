def _install():
    from ..core import DATAFRAME_TYPE, SERIES_TYPE, INDEX_TYPE
    from .standardize_range_index import ChunkStandardizeRangeIndex
    from .string_ import _string_method_to_handlers
    from .datetimes import _datetime_method_to_handlers
    from .accessor import StringAccessor, DatetimeAccessor, CachedAccessor

    for t in DATAFRAME_TYPE:
        setattr(t, 'to_gpu', to_gpu)
        setattr(t, 'to_cpu', to_cpu)
        setattr(t, 'rechunk', rechunk)
        setattr(t, 'describe', describe)
        setattr(t, 'apply', df_apply)
        setattr(t, 'transform', df_transform)
        setattr(t, 'fillna', fillna)
        setattr(t, 'ffill', ffill)
        setattr(t, 'bfill', bfill)
        setattr(t, 'isin', df_isin)
        setattr(t, 'isna', isna)
        setattr(t, 'isnull', isnull)
        setattr(t, 'notna', notna)
        setattr(t, 'notnull', notnull)
        setattr(t, 'dropna', df_dropna)
        setattr(t, 'shift', shift)
        setattr(t, 'tshift', tshift)
        setattr(t, 'diff', df_diff)
        setattr(t, 'astype', astype)
        setattr(t, 'drop', df_drop)
        setattr(t, 'pop', df_pop)
        setattr(t, '__delitem__', lambda df, items: df_drop(df, items, axis=1, inplace=True))
        setattr(t, 'drop_duplicates', df_drop_duplicates)
        setattr(t, 'melt', melt)
        setattr(t, 'memory_usage', df_memory_usage)
        setattr(t, 'select_dtypes', select_dtypes)
        setattr(t, 'map_chunk', map_chunk)
        setattr(t, 'rebalance', rebalance)
        setattr(t, 'stack', stack)
        setattr(t, 'explode', df_explode)

    for t in SERIES_TYPE:
        setattr(t, 'to_gpu', to_gpu)
        setattr(t, 'to_cpu', to_cpu)
        setattr(t, 'rechunk', rechunk)
        setattr(t, 'map', map_)
        setattr(t, 'describe', describe)
        setattr(t, 'apply', series_apply)
        setattr(t, 'transform', series_transform)
        setattr(t, 'fillna', fillna)
        setattr(t, 'ffill', ffill)
        setattr(t, 'bfill', bfill)
        setattr(t, 'isin', series_isin)
        setattr(t, 'isna', isna)
        setattr(t, 'isnull', isnull)
        setattr(t, 'notna', notna)
        setattr(t, 'notnull', notnull)
        setattr(t, 'dropna', series_dropna)
        setattr(t, 'shift', shift)
        setattr(t, 'tshift', tshift)
        setattr(t, 'diff', series_diff)
        setattr(t, 'value_counts', value_counts)
        setattr(t, 'astype', astype)
        setattr(t, 'drop', series_drop)
        setattr(t, 'drop_duplicates', series_drop_duplicates)
        setattr(t, 'memory_usage', series_memory_usage)
        setattr(t, 'map_chunk', map_chunk)
        setattr(t, 'rebalance', rebalance)
        setattr(t, 'explode', series_explode)

    for t in INDEX_TYPE:
        setattr(t, 'rechunk', rechunk)
        setattr(t, 'drop', index_drop)
        setattr(t, 'drop_duplicates', index_drop_duplicates)
        setattr(t, 'memory_usage', index_memory_usage)

    for method in _string_method_to_handlers:
        if not hasattr(StringAccessor, method):
            StringAccessor._register(method)

    for method in _datetime_method_to_handlers:
        if not hasattr(DatetimeAccessor, method):
            DatetimeAccessor._register(method)

    for series in SERIES_TYPE:
        series.str = CachedAccessor('str', StringAccessor)
        series.dt = CachedAccessor('dt', DatetimeAccessor)