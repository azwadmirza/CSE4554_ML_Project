    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False,
                 chunk_size=None, gpu=None, sparse=None):
        if isinstance(data, TENSOR_TYPE):
            if chunk_size is not None:
                data = data.rechunk(chunk_size)
            df = dataframe_from_tensor(data, index=index, columns=columns, gpu=gpu, sparse=sparse)
        elif isinstance(data, DATAFRAME_TYPE):
            if not hasattr(data, 'data'):
                # DataFrameData
                df = _Frame(data)
            else:
                df = data
        elif isinstance(data, dict) and any(isinstance(v, (Base, Entity)) for v in data.values()):
            # data is a dict and some value is tensor
            columns = list(data.keys()) if columns is None else columns
            tensors = []
            for c in columns:
                tensors.append(astensor(data[c]))
            df = dataframe_from_1d_tensors(
                tensors, index=index, columns=columns,
                gpu=gpu, sparse=sparse)
        else:
            pdf = pd.DataFrame(data, index=index, columns=columns, dtype=dtype, copy=copy)
            df = from_pandas_df(pdf, chunk_size=chunk_size, gpu=gpu, sparse=sparse)
        super().__init__(df.data)