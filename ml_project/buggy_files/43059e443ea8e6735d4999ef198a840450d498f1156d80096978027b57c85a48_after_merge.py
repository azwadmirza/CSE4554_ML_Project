    def derive_subtype(
        self,
        schema: s_schema.Schema,
        *,
        name: s_name.QualName,
        attrs: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> typing.Tuple[s_schema.Schema, TupleExprAlias]:
        assert not kwargs
        return TupleExprAlias.from_subtypes(
            schema,
            dict(self.iter_subtypes(schema)),
            self.get_typemods(schema),
            name=name,
            **(attrs or {}),
        )