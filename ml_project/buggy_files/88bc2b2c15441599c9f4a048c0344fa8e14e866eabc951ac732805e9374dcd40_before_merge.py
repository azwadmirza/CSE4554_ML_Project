    def _serialize_multi_index(index):
        kw = _extract_property(index, IndexValue.MultiIndex, store_data)
        kw['_sortorder'] = index.sortorder
        return IndexValue.MultiIndex(**kw)