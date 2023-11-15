    def create_mp_lock(cls):
        if not hasattr(cls, 'mp_lock'):
            try:
                from multiprocessing import RLock
                cls.mp_lock = RLock()  # multiprocessing lock
            except ImportError:  # pragma: no cover
                cls.mp_lock = None
            except OSError:  # pragma: no cover
                cls.mp_lock = None