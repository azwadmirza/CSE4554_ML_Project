    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._style = self._style_name = None
        self._detyped = None