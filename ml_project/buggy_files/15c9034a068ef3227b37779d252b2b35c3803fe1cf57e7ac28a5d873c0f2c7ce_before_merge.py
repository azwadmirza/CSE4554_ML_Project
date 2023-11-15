    def __new__(cls, lsttype=None, meminfo=None, allocated=None):
        if config.DISABLE_JIT:
            return list.__new__(list)
        else:
            return object.__new__(cls)