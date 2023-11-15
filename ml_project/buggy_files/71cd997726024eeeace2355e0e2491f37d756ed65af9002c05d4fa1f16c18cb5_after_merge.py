    def __init__(self, data=None, index=None, dtype=None, name=None, copy=False,
                 chunk_size=None, gpu=None, sparse=None, num_partitions=None):
        # make sure __getattr__ does not result in stack overflow
        self._data = None

        if dtype is not None:
            dtype = np.dtype(dtype)

        need_repart = False
        if isinstance(data, (TENSOR_TYPE, INDEX_TYPE)):
            if chunk_size is not None:
                data = data.rechunk(chunk_size)
            name = name or getattr(data, 'name', None)
            series = series_from_tensor(data, index=index, name=name, gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        elif isinstance(index, INDEX_TYPE):
            if data is not None:
                data = astensor(data, chunk_size=chunk_size)
            series = series_from_tensor(data, index=index, name=name,
                                        dtype=dtype, gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        elif isinstance(data, SERIES_TYPE):
            if not hasattr(data, 'data'):
                # SeriesData
                series = _Series(data)
            else:
                series = data
            need_repart = num_partitions is not None
        else:
            pd_series = pd.Series(data, index=index, dtype=dtype, name=name, copy=copy)
            if num_partitions is not None:
                chunk_size = ceildiv(len(pd_series), num_partitions)
            series = from_pandas_series(pd_series, chunk_size=chunk_size, gpu=gpu, sparse=sparse)

        if need_repart:
            series = series.rebalance(num_partitions=num_partitions)
        super().__init__(series.data)