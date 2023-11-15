    def _alter_finalize(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        schema = self._finalize_affected_refs(schema, context)
        return schema