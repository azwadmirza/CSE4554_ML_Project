    def create_shell(
        cls,
        schema: s_schema.Schema,
        *,
        subtypes: Mapping[str, TypeShell],
        typemods: Any = None,
        name: Optional[s_name.Name] = None,
    ) -> TupleTypeShell:
        if name is None:
            name = s_name.UnqualName(name='__unresolved__')

        return TupleTypeShell(
            subtypes=subtypes,
            typemods=typemods,
            name=name,
            schemaclass=cls,
        )