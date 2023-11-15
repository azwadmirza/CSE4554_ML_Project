    def __init__(self, imp, context, sig):
        self._callable = _wrap_missing_loc(imp)
        self._imp = self._callable()
        self._context = context
        self._sig = sig