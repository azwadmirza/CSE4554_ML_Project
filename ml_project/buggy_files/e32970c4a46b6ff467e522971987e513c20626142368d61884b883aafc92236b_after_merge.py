    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False,
                 chunk_size=None, gpu=None, sparse=None, num_partitions=None):
        # make sure __getattr__ does not result in stack overflow
        self._data = None

        need_repart = False
        if isinstance(data, TENSOR_TYPE):
            if chunk_size is not None:
                data = data.rechunk(chunk_size)
            df = dataframe_from_tensor(data, index=index, columns=columns, gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        elif isinstance(data, SERIES_TYPE):
            df = data.to_frame()
            need_repart = num_partitions is not None
        elif isinstance(data, DATAFRAME_TYPE):
            if not hasattr(data, 'data'):
                # DataFrameData
                df = _Frame(data)
            else:
                df = data
            need_repart = num_partitions is not None
        elif isinstance(data, dict) and any(isinstance(v, (Base, Entity)) for v in data.values()):
            # data is a dict and some value is tensor
            df = dataframe_from_1d_tileables(
                data, index=index, columns=columns, gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        elif isinstance(data, list) and any(isinstance(v, (Base, Entity)) for v in data):
            # stack data together
            data = stack(data)
            df = dataframe_from_tensor(data, index=index, columns=columns,
                                       gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        elif isinstance(index, (INDEX_TYPE, SERIES_TYPE)):
            if isinstance(data, dict):
                data = {k: astensor(v, chunk_size=chunk_size) for k, v in data.items()}
                df = dataframe_from_1d_tileables(data, index=index, columns=columns,
                                                 gpu=gpu, sparse=sparse)
            else:
                if data is not None:
                    data = astensor(data, chunk_size=chunk_size)
                df = dataframe_from_tensor(data, index=index,
                                           columns=columns, gpu=gpu, sparse=sparse)
            need_repart = num_partitions is not None
        else:
            pdf = pd.DataFrame(data, index=index, columns=columns, dtype=dtype, copy=copy)
            if num_partitions is not None:
                chunk_size = ceildiv(len(pdf), num_partitions)
            df = from_pandas_df(pdf, chunk_size=chunk_size, gpu=gpu, sparse=sparse)

        if need_repart:
            df = df.rebalance(num_partitions=num_partitions)
        super().__init__(df.data)