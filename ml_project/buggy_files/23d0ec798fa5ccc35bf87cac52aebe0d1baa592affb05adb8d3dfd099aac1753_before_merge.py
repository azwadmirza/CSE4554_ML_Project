    def __init__(self, event: CallableEvents, filter: Callable):
        if not callable(filter):
            raise TypeError("Argument filter should be callable")
        self.event = event
        self.filter = filter