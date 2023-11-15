    def from_subtypes(
        cls: typing.Type[Array_T],
        schema: s_schema.Schema,
        subtypes: Sequence[Type],
        typemods: Any = None,
        *,
        name: Optional[s_name.QualName] = None,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Array_T]:
        if len(subtypes) != 1:
            raise errors.SchemaError(
                f'unexpected number of subtypes, expecting 1: {subtypes!r}')
        stype = subtypes[0]

        if isinstance(stype, Array):
            raise errors.UnsupportedFeatureError(
                f'nested arrays are not supported')

        # One-dimensional unbounded array.
        dimensions = [-1]

        return cls.create(
            schema,
            element_type=stype,
            dimensions=dimensions,
            name=name,
            **kwargs,
        )