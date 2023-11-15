    def __init__(self, context, handle, info_log, finalizer=None):
        self.context = context
        self.handle = handle
        self.info_log = info_log
        self.finalizer = finalizer
        self.is_managed = self.finalizer is not None