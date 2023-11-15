def all(a, axis=None, out=None, keepdims=False):
    assert isinstance(a, cupy.ndarray)
    return a.all(axis=axis, out=out, keepdims=keepdims)