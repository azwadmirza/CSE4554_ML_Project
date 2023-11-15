    def __init__(self) -> None:
        self._lock = trio.Lock()