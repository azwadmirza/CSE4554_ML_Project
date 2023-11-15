    def __init__(self) -> None:
        super().__init__(set)
        self.alias: DefaultDict[Optional[str], Dict[str, str]] = defaultdict(dict)