def any(a, axis=None, out=None, keepdims=False):
    assert isinstance(a, cupy.ndarray)
    return a.any(axis=axis, out=out, keepdims=keepdims)