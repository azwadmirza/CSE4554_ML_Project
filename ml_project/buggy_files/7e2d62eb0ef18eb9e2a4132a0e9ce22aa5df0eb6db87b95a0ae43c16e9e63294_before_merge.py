    def derive_subtype(
        self,
        schema: s_schema.Schema,
        *,
        name: s_name.QualName,
        attrs: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, Array]:
        assert not kwargs
        return Array.from_subtypes(
            schema,
            [self.get_element_type(schema)],
            self.get_typemods(schema),
            name=name,
            **(attrs or {}),
        )