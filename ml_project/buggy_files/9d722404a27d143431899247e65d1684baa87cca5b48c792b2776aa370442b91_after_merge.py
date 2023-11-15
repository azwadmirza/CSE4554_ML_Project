def scalar(data, dtype=None, gpu=False):
    try:
        arr = np.array(data, dtype=dtype)
        op = Scalar(arr.item(), dtype=arr.dtype, gpu=gpu)
        shape = ()
        return op(shape)
    except ValueError:
        raise TypeError('Expect scalar, got: {0}'.format(data))