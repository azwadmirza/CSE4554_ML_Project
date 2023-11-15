    def __init__(self, fail: Callable[[str, Context], None]) -> None:
        self.fail = fail