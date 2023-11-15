    def __init__(
        self,
        *,
        components: Iterable[TypeShell],
        module: str,
        opaque: bool = False,
        schemaclass: typing.Type[Type] = Type,
        sourcectx: Optional[parsing.ParserContext] = None,
    ) -> None:
        super().__init__(
            components=components,
            module=module,
            schemaclass=schemaclass,
            sourcectx=sourcectx,
        )
        self.opaque = opaque