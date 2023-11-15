    def apply(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        if self.if_exists:
            scls = self.get_object(schema, context, default=None)
            if scls is None:
                context.current().op.discard(self)
                return schema
        else:
            scls = self.get_object(schema, context)

        self.scls = scls

        with self.new_context(schema, context, scls):
            if (
                not self.canonical
                and self.if_unused
                and self._has_outside_references(schema, context)
            ):
                parent_ctx = context.parent()
                if parent_ctx is not None:
                    parent_ctx.op.discard(self)

                return schema

            schema = self._delete_begin(schema, context)
            schema = self._delete_innards(schema, context)
            schema = self._delete_finalize(schema, context)

        return schema