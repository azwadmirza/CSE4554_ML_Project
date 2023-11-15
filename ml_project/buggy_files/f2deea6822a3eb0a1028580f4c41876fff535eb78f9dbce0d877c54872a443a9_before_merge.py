    def __new__(cls, opts, functions, returners=None, intervals=None, cleanup=None):
        '''
        Only create one instance of Schedule
        '''
        if cls.instance is None:
            log.debug('Initializing new Schedule')
            # we need to make a local variable for this, as we are going to store
            # it in a WeakValueDictionary-- which will remove the item if no one
            # references it-- this forces a reference while we return to the caller
            cls.instance = object.__new__(cls)
            cls.instance.__singleton_init__(opts, functions, returners, intervals, cleanup)
        else:
            log.debug('Re-using Schedule')
        return cls.instance