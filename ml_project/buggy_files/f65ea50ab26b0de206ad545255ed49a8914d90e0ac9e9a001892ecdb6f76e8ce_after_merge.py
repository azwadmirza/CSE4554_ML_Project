    def __init__(
        self,
        *,
        components: Iterable[TypeShell],
        module: str,
        schemaclass: typing.Type[Type] = Type,
        sourcectx: Optional[parsing.ParserContext] = None,
    ) -> None:
        super().__init__(
            name=s_name.UnqualName('__unresolved__'),
            schemaclass=schemaclass,
            sourcectx=sourcectx,
        )
        self.components = tuple(components)
        self.module = module