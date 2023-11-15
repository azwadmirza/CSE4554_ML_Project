    def __init__(self, context, handle, info_log, finalizer=None):
        self.context = context
        self.handle = handle
        self.info_log = info_log
        self.finalizer = finalizer
        if self.finalizer is not None:
            self._finalizer = utils.finalize(self, finalizer)