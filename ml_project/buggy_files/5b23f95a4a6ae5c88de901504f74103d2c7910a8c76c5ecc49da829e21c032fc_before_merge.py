    def __exit__(self, exc_type: Type[Exception], exc_value: Exception, traceback: Any) -> bool:  # NOQA
        self.disable()
        return True