    def _alter_begin(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
    ) -> s_schema.Schema:
        orig_schema = schema
        orig_rec = context.current().enable_recursion
        context.current().enable_recursion = False
        schema = super()._alter_begin(schema, context)
        context.current().enable_recursion = orig_rec
        scls = self.scls

        vn = scls.get_verbosename(schema, with_parent=True)

        orig_target = scls.get_target(orig_schema)
        new_target = scls.get_target(schema)

        if new_target is None:
            # This will happen if `RESET TYPE` was called
            # on a non-inherited type.
            raise errors.SchemaError(
                f'cannot RESET TYPE of {vn} because it is not inherited',
                context=self.source_context,
            )

        if orig_target == new_target:
            return schema

        if not context.canonical:
            assert orig_target is not None
            assert new_target is not None
            ptr_op = self.get_parent_op(context)
            src_op = self.get_referrer_context_or_die(context).op

            if self._needs_cast_expr(
                schema=schema,
                ptr_op=ptr_op,
                src_op=src_op,
                old_type=orig_target,
                new_type=new_target,
            ):
                vn = scls.get_verbosename(schema, with_parent=True)
                ot = orig_target.get_verbosename(schema)
                nt = new_target.get_verbosename(schema)
                raise errors.SchemaError(
                    f'{vn} cannot be cast automatically from '
                    f'{ot} to {nt}',
                    hint=(
                        'You might need to specify a conversion '
                        'expression in a USING clause'
                    ),
                    context=self.source_context,
                )

            if self.cast_expr is not None:
                vn = scls.get_verbosename(schema, with_parent=True)
                self.cast_expr = self._compile_expr(
                    schema=orig_schema,
                    context=context,
                    expr=self.cast_expr,
                    target_as_singleton=True,
                    singleton_result_expected=True,
                    expr_description=(
                        f'the USING clause for the alteration of {vn}'
                    ),
                )

                using_type = self.cast_expr.stype
                if not using_type.assignment_castable_to(
                    new_target,
                    self.cast_expr.schema,
                ):
                    ot = using_type.get_verbosename(self.cast_expr.schema)
                    nt = new_target.get_verbosename(schema)
                    raise errors.SchemaError(
                        f'result of USING clause for the alteration of '
                        f'{vn} cannot be cast automatically from '
                        f'{ot} to {nt} ',
                        hint='You might need to add an explicit cast.',
                        context=self.source_context,
                    )

            schema = self._propagate_if_expr_refs(
                schema,
                context,
                action=self.get_friendly_description(schema=schema),
            )

            if orig_target is not None:
                if isinstance(orig_target, s_types.Collection):
                    parent_op = self.get_parent_op(context)
                    cleanup_op = orig_target.as_colltype_delete_delta(
                        schema, expiring_refs={scls})
                    parent_op.add(cleanup_op)
                    schema = cleanup_op.apply(schema, context)
                elif orig_target.is_compound_type(schema):
                    parent_op = self.get_parent_op(context)
                    cleanup_op = orig_target.init_delta_command(
                        schema,
                        sd.DeleteObject,
                        if_unused=True,
                        expiring_refs={scls},
                    )
                    parent_op.add(cleanup_op)
                    schema = cleanup_op.apply(schema, context)

            if context.enable_recursion:
                schema = self._propagate_ref_field_alter_in_inheritance(
                    schema,
                    context,
                    field_name='target',
                )

        return schema