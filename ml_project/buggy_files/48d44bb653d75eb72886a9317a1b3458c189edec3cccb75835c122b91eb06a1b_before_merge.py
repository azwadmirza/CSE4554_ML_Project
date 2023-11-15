    def run(self, fun, *args, **kwargs) -> Awaitable:
        return wrap_future(self.executor.submit(self.__run_transaction, fun, *args, **kwargs))