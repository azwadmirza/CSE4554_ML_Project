    def _alter_innards(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        if not context.canonical:
            self._canonicalize(schema, context, self.scls)
        return super()._alter_innards(schema, context)