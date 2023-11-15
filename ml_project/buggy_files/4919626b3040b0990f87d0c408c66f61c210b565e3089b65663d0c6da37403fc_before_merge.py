    def _alter_innards(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        for op in self.get_subcommands(include_prerequisites=False):
            if not isinstance(op, AlterObjectProperty):
                schema = op.apply(schema, context=context)

        return schema