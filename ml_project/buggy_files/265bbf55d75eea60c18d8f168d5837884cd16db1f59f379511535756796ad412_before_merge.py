    def __init__(self, dtype=None, to_fetch_key=None, **kw):
        super(TensorFetch, self).__init__(
            _dtype=dtype, _to_fetch_key=to_fetch_key, **kw)