    def executescript(self, script: str) -> Awaitable:
        return wrap_future(self.executor.submit(self.connection.executescript, script))