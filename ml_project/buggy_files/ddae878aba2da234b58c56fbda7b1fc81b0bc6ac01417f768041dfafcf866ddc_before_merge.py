    def __init__(self, task, loop):
        self._loop = loop
        self.task = task
        self.done = asyncio.Event()