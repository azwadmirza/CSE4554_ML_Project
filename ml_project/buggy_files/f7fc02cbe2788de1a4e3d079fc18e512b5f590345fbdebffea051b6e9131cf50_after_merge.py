    def create(
        cls: typing.Type[Array_T],
        schema: s_schema.Schema,
        *,
        name: Optional[s_name.Name] = None,
        id: Optional[uuid.UUID] = None,
        dimensions: Sequence[int] = (),
        element_type: Any,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Array_T]:
        if not dimensions:
            dimensions = [-1]

        if dimensions != [-1]:
            raise errors.UnsupportedFeatureError(
                f'multi-dimensional arrays are not supported')

        if name is None:
            name = cls.generate_name(element_type.get_name(schema))

        if isinstance(name, s_name.QualName):
            result = schema.get(name, type=cls, default=None)
        else:
            result = schema.get_global(cls, name, default=None)

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