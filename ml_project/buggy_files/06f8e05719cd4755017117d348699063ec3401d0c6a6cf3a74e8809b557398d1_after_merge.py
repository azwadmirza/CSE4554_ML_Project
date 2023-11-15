    def create(
        cls: typing.Type[Tuple_T],
        schema: s_schema.Schema,
        *,
        name: Optional[s_name.Name] = None,
        id: Optional[uuid.UUID] = None,
        element_types: Mapping[str, Type],
        named: bool = False,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Tuple_T]:
        el_types = so.ObjectDict[str, Type].create(schema, element_types)
        if name is None:
            name = cls.generate_name(
                {n: el.get_name(schema) for n, el in element_types.items()},
                named,
            )

        if isinstance(name, s_name.QualName):
            result = schema.get(name, type=cls, default=None)
        else:
            result = schema.get_global(cls, name, default=None)

        if result is None:
            schema, result = super().create_in_schema(
                schema,
                id=id,
                name=name,
                named=named,
                element_types=el_types,
                **kwargs,
            )

        return schema, result