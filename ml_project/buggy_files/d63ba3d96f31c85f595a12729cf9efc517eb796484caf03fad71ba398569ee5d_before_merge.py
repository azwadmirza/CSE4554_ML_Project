def build_series(series_obj, fill_value=1, size=1):
    empty_series = build_empty_series(series_obj.dtype, index=series_obj.index_value.to_pandas()[:0])
    record = _generate_value(series_obj.dtype, fill_value)
    if isinstance(empty_series.index, pd.MultiIndex):
        index = tuple(_generate_value(level.dtype, fill_value) for level in empty_series.index.levels)
        empty_series.loc[index, ] = record
    else:
        if isinstance(empty_series.index.dtype, pd.CategoricalDtype):
            index = None
        else:
            index = _generate_value(empty_series.index.dtype, fill_value)
        empty_series.loc[index] = record

    empty_series = pd.concat([empty_series] * size)
    # make sure dtype correct for MultiIndex
    empty_series = empty_series.astype(series_obj.dtype, copy=False)
    return empty_series