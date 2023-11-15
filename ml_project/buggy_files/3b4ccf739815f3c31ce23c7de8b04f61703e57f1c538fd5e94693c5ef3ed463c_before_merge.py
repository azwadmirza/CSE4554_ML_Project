    def __init__(self, strategy: Callable[[Iterable[T]], T]) -> None:
        self.strategy = strategy