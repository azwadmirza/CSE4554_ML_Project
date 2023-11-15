    def __init__(self):
        # Create global parallelism locks to avoid racing issues with parallel
        # bars works only if fork available (Linux/MacOSX, but not Windows)
        cls = type(self)
        root_lock = cls.th_lock
        if root_lock is not None:
            root_lock.acquire()
        cls.create_mp_lock()
        if root_lock is not None:
            root_lock.release()
        self.locks = [lk for lk in [cls.mp_lock, cls.th_lock] if lk is not None]