    def __init__(self, to_fetch_key=None, **kw):
        kw.pop('output_types', None)
        kw.pop('_output_types', None)
        super().__init__(_to_fetch_key=to_fetch_key, **kw)