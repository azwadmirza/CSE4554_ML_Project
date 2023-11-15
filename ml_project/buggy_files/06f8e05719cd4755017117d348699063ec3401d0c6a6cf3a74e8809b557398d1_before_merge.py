    def create(
        cls: typing.Type[Tuple_T],
        schema: s_schema.Schema,
        *,
        name: Optional[s_name.Name] = None,
        id: Union[uuid.UUID, so.NoDefaultT] = so.NoDefault,
        element_types: Mapping[str, Type],
        named: bool = False,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Tuple_T]:
        element_types = types.MappingProxyType(element_types)
        if id is so.NoDefault:
            quals = []
            if name is not None:
                quals.append(str(name))
            id = generate_tuple_type_id(schema, element_types, named, *quals)

        if name is None:
            st_names = ', '.join(
                st.get_displayname(schema) for st in element_types.values()
            )
            name = type_name_from_id_and_displayname(id, f'tuple<{st_names}>')

        result = typing.cast(Tuple_T, schema.get_by_id(id, default=None))
        if result is None:
            schema, result = super().create_in_schema(
                schema,
                id=id,
                name=name,
                named=named,
                element_types=element_types,
                **kwargs,
            )

        return schema, result