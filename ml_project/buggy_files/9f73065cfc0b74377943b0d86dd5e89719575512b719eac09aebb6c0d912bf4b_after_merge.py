    def __init__(self) -> None:
        self._locks = {}
        self._reference_counts = defaultdict(int)