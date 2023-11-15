    def __new__(cls, *args, **kwargs):
        ''' Create a new instance
        '''
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst