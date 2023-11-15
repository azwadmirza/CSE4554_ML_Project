    def __init__(
        self,
        *,
        name: s_name.Name,
        expr: Optional[str] = None,
        subtypes: Mapping[str, TypeShell],
        typemods: Any = None,
    ) -> None:
        super().__init__(name=name, schemaclass=Tuple, expr=expr)
        self.subtypes = subtypes
        self.typemods = typemods