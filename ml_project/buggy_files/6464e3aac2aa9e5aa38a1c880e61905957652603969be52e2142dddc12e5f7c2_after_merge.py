    def __init__(self, pooled_function, args, kwargs, update=None, error_handling=True):
        self.pooled_function = pooled_function
        self.args = args
        self.kwargs = kwargs
        self.update = update
        self.error_handling = error_handling
        self.done = Event()
        self._result = None
        self._exception = None