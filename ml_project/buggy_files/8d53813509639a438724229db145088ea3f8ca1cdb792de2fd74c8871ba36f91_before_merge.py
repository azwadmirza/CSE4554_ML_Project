    def __init__(self):
        # Create global parallelism locks to avoid racing issues with parallel
        # bars works only if fork available (Linux/MacOSX, but not Windows)
        self.create_mp_lock()
        self.create_th_lock()
        cls = type(self)
        self.locks = [lk for lk in [cls.mp_lock, cls.th_lock] if lk is not None]