    def run(self, fun, *args, **kwargs) -> Awaitable:
        return asyncio.get_event_loop().run_in_executor(
            self.executor, lambda: self.__run_transaction(fun, *args, **kwargs)
        )