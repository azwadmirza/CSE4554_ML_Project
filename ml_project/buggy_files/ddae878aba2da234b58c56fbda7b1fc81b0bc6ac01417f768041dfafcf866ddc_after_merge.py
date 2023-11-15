    def __init__(self, operation, return_type, loop):
        self.operation = IAsyncOperation[return_type](operation)
        self.done = asyncio.Event()
        self.return_type = return_type
        self._loop = loop