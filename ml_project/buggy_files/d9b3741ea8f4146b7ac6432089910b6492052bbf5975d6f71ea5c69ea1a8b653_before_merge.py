    def __init__(self, fail: Callable[[str, Context], None],
                 start: Union[Node, SymbolTableNode], warn: bool) -> None:
        self.seen = []  # type: List[Type]
        self.fail = fail
        self.start = start
        self.warn = warn