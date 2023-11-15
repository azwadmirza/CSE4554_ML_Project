    def create_th_lock(cls):
        if not hasattr(cls, 'th_lock'):
            try:
                cls.th_lock = th.RLock()  # thread lock
            except OSError:  # pragma: no cover
                cls.th_lock = None