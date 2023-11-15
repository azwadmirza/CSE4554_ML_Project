    def as_delete_delta(
        self,
        *,
        schema: s_schema.Schema,
        context: so.ComparisonContext,
    ) -> sd.ObjectCommand[Constraint]:
        return super().as_delete_delta(schema=schema, context=context)