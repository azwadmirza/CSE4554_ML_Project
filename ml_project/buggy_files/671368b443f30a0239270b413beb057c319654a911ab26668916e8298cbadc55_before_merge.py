def dataframe_from_tensor(tensor, index=None, columns=None, gpu=None, sparse=False):
    if tensor.ndim > 2 or tensor.ndim <= 0:
        raise TypeError(f'Not support create DataFrame from {tensor.ndim} dims tensor')
    try:
        col_num = tensor.shape[1]
    except IndexError:
        col_num = 1
    gpu = tensor.op.gpu if gpu is None else gpu
    op = DataFrameFromTensor(input_=tensor,
                             dtypes=pd.Series([tensor.dtype] * col_num, index=columns),
                             gpu=gpu, sparse=sparse)
    return op(tensor, index, columns)