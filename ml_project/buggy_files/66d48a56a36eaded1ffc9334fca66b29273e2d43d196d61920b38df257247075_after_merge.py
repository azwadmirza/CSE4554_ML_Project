    def __init__(
        self,
        *,
        search_path: Iterable[str],
        binary_name: str,
        test: Optional[BinaryPathTest] = None,
    ) -> None:
        self.search_path = tuple(OrderedSet(search_path))
        self.binary_name = binary_name
        self.test = test