    def canonicalize_attributes(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
    ) -> s_schema.Schema:
        schema = super().canonicalize_attributes(schema, context)
        target_ref = self.get_local_attribute_value('target')
        inf_target_ref: Optional[s_types.TypeShell]

        # When cardinality/required is altered, we need to force a
        # reconsideration of expr if it exists in order to check
        # it against the new specifier or compute them on a
        # RESET. This is kind of unfortunate.
        if (
            isinstance(self, sd.AlterObject)
            and (self.has_attribute_value('cardinality')
                 or self.has_attribute_value('required'))
            and not self.has_attribute_value('expr')
            and (expr := self.scls.get_expr(schema)) is not None
        ):
            self.set_attribute_value(
                'expr',
                s_expr.Expression.not_compiled(expr)
            )

        if isinstance(target_ref, ComputableRef):
            schema, inf_target_ref, base = self._parse_computable(
                target_ref.expr, schema, context)
        elif (expr := self.get_local_attribute_value('expr')) is not None:
            schema, inf_target_ref, base = self._parse_computable(
                expr.qlast, schema, context)
        else:
            inf_target_ref = None
            base = None

        if base is not None:
            self.set_attribute_value(
                'bases', so.ObjectList.create(schema, [base]),
            )

            self.set_attribute_value(
                'is_derived', True
            )

            if context.declarative:
                self.set_attribute_value(
                    'declared_overloaded', True
                )

        if inf_target_ref is not None:
            srcctx = self.get_attribute_source_context('target')
            self.set_attribute_value(
                'target',
                inf_target_ref,
                source_context=srcctx,
            )

        schema = s_types.materialize_type_in_attribute(
            schema, context, self, 'target')

        expr = self.get_local_attribute_value('expr')
        if expr is not None:
            # There is an expression, therefore it is a computable.
            self.set_attribute_value('computable', True)

        return schema