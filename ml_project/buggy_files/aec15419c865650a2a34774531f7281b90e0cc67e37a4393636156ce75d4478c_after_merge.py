    def __init__(self, dtype=None, to_fetch_key=None, sparse=False, **kw):
        kw.pop('output_types', None)
        kw.pop('_output_types', None)
        super().__init__(
            _dtype=dtype, _to_fetch_key=to_fetch_key, _sparse=sparse, **kw)