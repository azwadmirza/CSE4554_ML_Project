    def __init__(self) -> None:
        self.registry = SphinxComponentRegistry()
        self.messagelog = []  # type: List[str]
        self.verbosity = 0