def parse_index(index_value, *args, store_data=False, key=None):
    from .core import IndexValue

    def _extract_property(index, tp, ret_data):
        kw = {
            '_min_val': _get_index_min(index),
            '_max_val': _get_index_max(index),
            '_min_val_close': True,
            '_max_val_close': True,
            '_key': key or _tokenize_index(index, *args),
        }
        if ret_data:
            kw['_data'] = index.values
        for field in tp._FIELDS:
            if field in kw or field == '_data':
                continue
            val = getattr(index, field.lstrip('_'), None)
            if val is not None:
                kw[field] = val
        return kw

    def _tokenize_index(index, *token_objects):
        if not index.empty:
            return tokenize(index)
        else:
            return tokenize(index, *token_objects)

    def _get_index_min(index):
        try:
            return index.min()
        except ValueError:
            if isinstance(index, pd.IntervalIndex):
                return None
            raise
        except TypeError:
            return None

    def _get_index_max(index):
        try:
            return index.max()
        except ValueError:
            if isinstance(index, pd.IntervalIndex):
                return None
            raise
        except TypeError:
            return None

    def _serialize_index(index):
        tp = getattr(IndexValue, type(index).__name__)
        properties = _extract_property(index, tp, store_data)
        return tp(**properties)

    def _serialize_range_index(index):
        if is_pd_range_empty(index):
            properties = {
                '_is_monotonic_increasing': True,
                '_is_monotonic_decreasing': False,
                '_is_unique': True,
                '_min_val': _get_index_min(index),
                '_max_val': _get_index_max(index),
                '_min_val_close': True,
                '_max_val_close': False,
                '_key': key or _tokenize_index(index, *args),
                '_name': index.name,
                '_dtype': index.dtype,
            }
        else:
            properties = _extract_property(index, IndexValue.RangeIndex, False)
        return IndexValue.RangeIndex(_slice=slice(_get_range_index_start(index),
                                                  _get_range_index_stop(index),
                                                  _get_range_index_step(index)),
                                     **properties)

    def _serialize_multi_index(index):
        kw = _extract_property(index, IndexValue.MultiIndex, store_data)
        kw['_sortorder'] = index.sortorder
        kw['_dtypes'] = [lev.dtype for lev in index.levels]
        return IndexValue.MultiIndex(**kw)

    if index_value is None:
        return IndexValue(_index_value=IndexValue.Index(
            _is_monotonic_increasing=False,
            _is_monotonic_decreasing=False,
            _is_unique=False,
            _min_val=None,
            _max_val=None,
            _min_val_close=True,
            _max_val_close=True,
            _key=key or tokenize(*args),
        ))
    if isinstance(index_value, pd.RangeIndex):
        return IndexValue(_index_value=_serialize_range_index(index_value))
    elif isinstance(index_value, pd.MultiIndex):
        return IndexValue(_index_value=_serialize_multi_index(index_value))
    else:
        return IndexValue(_index_value=_serialize_index(index_value))