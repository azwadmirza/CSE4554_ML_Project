    def validate_alter(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> None:
        self._validate_legal_command(schema, context)