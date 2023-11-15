def series_from_tensor(tensor, index=None, name=None, gpu=None, sparse=False):
    if tensor.ndim > 1 or tensor.ndim <= 0:
        raise TypeError(f'Not support create DataFrame from {tensor.ndim} dims tensor')
    gpu = tensor.op.gpu if gpu is None else gpu
    op = SeriesFromTensor(dtype=tensor.dtype, gpu=gpu, sparse=sparse)
    return op(tensor, index, name)