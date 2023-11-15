    def __init__(
        self,
        components: Iterable[TypeShell],
        module: str,
    ) -> None:
        self.components = tuple(components)
        self.module = module