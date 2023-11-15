    def create_th_lock(cls):
        assert hasattr(cls, 'th_lock')
        warn("create_th_lock not needed anymore", TqdmDeprecationWarning,
             stacklevel=2)