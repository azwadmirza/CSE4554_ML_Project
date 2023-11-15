    def resolve_lookup_into_field(self, model_cls: Type[Model], lookup: str) -> Union[Field, ForeignObjectRel]:
        query = Query(model_cls)
        lookup_parts, field_parts, is_expression = query.solve_lookup_type(lookup)
        if lookup_parts:
            raise LookupsAreUnsupported()

        return self._resolve_field_from_parts(field_parts, model_cls)