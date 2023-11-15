    def create(
        cls: typing.Type[Array_T],
        schema: s_schema.Schema,
        *,
        name: Optional[s_name.Name] = None,
        id: Union[uuid.UUID, so.NoDefaultT] = so.NoDefault,
        dimensions: Sequence[int] = (),
        element_type: Any,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Array_T]:
        if not dimensions:
            dimensions = [-1]

        if dimensions != [-1]:
            raise errors.UnsupportedFeatureError(
                f'multi-dimensional arrays are not supported')

        if id is so.NoDefault:
            quals = []
            if name is not None:
                quals.append(str(name))
            id = generate_array_type_id(
                schema, element_type, dimensions, *quals)

        if name is None:
            dn = f'array<{element_type.get_displayname(schema)}>'
            name = type_name_from_id_and_displayname(id, dn)

        result = typing.cast(Array_T, schema.get_by_id(id, default=None))
        if result is None:
            schema, result = super().create_in_schema(
                schema,
                id=id,
                name=name,
                element_type=element_type,
                dimensions=dimensions,
                **kwargs,
            )

        return schema, result