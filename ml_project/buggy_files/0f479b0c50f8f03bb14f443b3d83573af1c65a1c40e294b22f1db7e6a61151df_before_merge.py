    def __init__(self, data=None, index=None, columns=None, default_kind=None,
                 default_fill_value=None, dtype=None, copy=False):

        # pick up the defaults from the Sparse structures
        if isinstance(data, SparseDataFrame):
            if index is None:
                index = data.index
            if columns is None:
                columns = data.columns
            if default_fill_value is None:
                default_fill_value = data.default_fill_value
            if default_kind is None:
                default_kind = data.default_kind
        elif isinstance(data, (SparseSeries, SparseArray)):
            if index is None:
                index = data.index
            if default_fill_value is None:
                default_fill_value = data.fill_value
            if columns is None and hasattr(data, 'name'):
                columns = [data.name]
            if columns is None:
                raise Exception("cannot pass a series w/o a name or columns")
            data = {columns[0]: data}

        if default_fill_value is None:
            default_fill_value = np.nan
        if default_kind is None:
            default_kind = 'block'

        self._default_kind = default_kind
        self._default_fill_value = default_fill_value

        if is_scipy_sparse(data):
            mgr = self._init_spmatrix(data, index, columns, dtype=dtype,
                                      fill_value=default_fill_value)
        elif isinstance(data, dict):
            mgr = self._init_dict(data, index, columns, dtype=dtype)
        elif isinstance(data, (np.ndarray, list)):
            mgr = self._init_matrix(data, index, columns, dtype=dtype)
        elif isinstance(data, SparseDataFrame):
            mgr = self._init_mgr(data._data,
                                 dict(index=index, columns=columns),
                                 dtype=dtype, copy=copy)
        elif isinstance(data, DataFrame):
            mgr = self._init_dict(data, data.index, data.columns, dtype=dtype)
        elif isinstance(data, BlockManager):
            mgr = self._init_mgr(data, axes=dict(index=index, columns=columns),
                                 dtype=dtype, copy=copy)
        elif data is None:
            data = DataFrame()

            if index is None:
                index = Index([])
            else:
                index = _ensure_index(index)

            if columns is None:
                columns = Index([])
            else:
                for c in columns:
                    data[c] = SparseArray(np.nan, index=index,
                                          kind=self._default_kind,
                                          fill_value=self._default_fill_value)
            mgr = to_manager(data, columns, index)
            if dtype is not None:
                mgr = mgr.astype(dtype)

        generic.NDFrame.__init__(self, mgr)