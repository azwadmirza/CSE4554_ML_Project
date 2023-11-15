    def run_with_foreign_keys_disabled(self, fun, *args, **kwargs) -> Awaitable:
        return asyncio.get_event_loop().run_in_executor(
            self.executor, self.__run_transaction_with_foreign_keys_disabled, fun, args, kwargs
        )