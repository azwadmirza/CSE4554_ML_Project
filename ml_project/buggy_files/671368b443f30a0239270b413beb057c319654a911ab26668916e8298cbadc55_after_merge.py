def dataframe_from_tensor(tensor, index=None, columns=None, gpu=None, sparse=False):
    if tensor is not None:
        if tensor.ndim > 2 or tensor.ndim <= 0:
            raise TypeError(f'Not support create DataFrame from {tensor.ndim} dims tensor')
        try:
            col_num = tensor.shape[1]
        except IndexError:
            col_num = 1
        gpu = tensor.op.gpu if gpu is None else gpu
        dtypes = pd.Series([tensor.dtype] * col_num, index=columns)
    else:
        gpu = None
        if columns is not None:
            dtypes = pd.Series([], index=columns)
        else:
            dtypes = pd.Series([], index=pd.Index([], dtype=object))
    op = DataFrameFromTensor(input_=tensor, dtypes=dtypes,
                             gpu=gpu, sparse=sparse)
    return op(tensor, index, columns)