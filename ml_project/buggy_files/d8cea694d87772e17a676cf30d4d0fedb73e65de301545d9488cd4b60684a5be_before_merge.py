    def _alter_begin(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        self._validate_legal_command(schema, context)

        for op in self.get_prerequisites():
            schema = op.apply(schema, context)

        if not context.canonical:
            schema = self.populate_ddl_identity(schema, context)
            schema = self.canonicalize_attributes(schema, context)
            computed_status = self._get_computed_status_of_fields(
                schema, context)
            self._update_computed_fields(schema, context, computed_status)
            self.validate_alter(schema, context)

        props = self.get_resolved_attributes(schema, context)
        schema = self.scls.update(schema, props)
        return schema