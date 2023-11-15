    def __init__(
        self,
        components: Iterable[TypeShell],
        module: str,
        opaque: bool = False,
    ) -> None:
        self.components = tuple(components)
        self.module = module
        self.opaque = opaque