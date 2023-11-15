    def __init__(self, imp, context, sig):
        self._imp = _wrap_missing_loc(imp)
        self._context = context
        self._sig = sig