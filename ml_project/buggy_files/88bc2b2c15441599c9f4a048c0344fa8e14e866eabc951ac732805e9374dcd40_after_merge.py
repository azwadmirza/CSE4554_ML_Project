    def _serialize_multi_index(index):
        kw = _extract_property(index, IndexValue.MultiIndex, store_data)
        kw['_sortorder'] = index.sortorder
        kw['_dtypes'] = [lev.dtype for lev in index.levels]
        return IndexValue.MultiIndex(**kw)