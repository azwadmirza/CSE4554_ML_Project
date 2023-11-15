    def run_with_foreign_keys_disabled(self, fun, *args, **kwargs) -> Awaitable:
        return wrap_future(
            self.executor.submit(self.__run_transaction_with_foreign_keys_disabled, fun, *args, **kwargs)
        )