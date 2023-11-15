    def __init__(
        self,
        *,
        name: s_name.Name,
        subtypes: Mapping[str, TypeShell],
        typemods: Any = None,
        schemaclass: typing.Type[Tuple] = Tuple,
    ) -> None:
        super().__init__(name=name, schemaclass=schemaclass)
        self.subtypes = subtypes
        self.typemods = typemods