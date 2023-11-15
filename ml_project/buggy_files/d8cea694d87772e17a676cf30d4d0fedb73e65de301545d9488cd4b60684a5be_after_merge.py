    def _alter_begin(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
    ) -> s_schema.Schema:
        scls = self.scls
        context.renames[self.classname] = self.new_name
        context.renamed_objs.add(scls)

        vn = scls.get_verbosename(schema)
        schema = self._propagate_if_expr_refs(
            schema,
            context,
            action=f'rename {vn}',
            fixer=self._fix_referencing_expr,
        )

        if not context.canonical:
            self.set_attribute_value(
                'name',
                value=self.new_name,
                orig_value=self.classname,
            )

        return super()._alter_begin(schema, context)