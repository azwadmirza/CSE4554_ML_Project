def series_from_tensor(tensor, index=None, name=None, dtype=None,
                       gpu=None, sparse=False):
    if tensor is not None:
        if tensor.ndim > 1 or tensor.ndim <= 0:
            raise TypeError(f'Not support create Series from {tensor.ndim} dims tensor')
        gpu = tensor.op.gpu if gpu is None else gpu
        dtype = dtype or tensor.dtype
    else:
        gpu = None
        dtype = dtype or np.dtype(float)
    op = SeriesFromTensor(input_=tensor, dtype=dtype, gpu=gpu, sparse=sparse)
    return op(tensor, index, name)