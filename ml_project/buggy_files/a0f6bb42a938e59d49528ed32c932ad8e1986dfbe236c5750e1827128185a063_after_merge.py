    def _get_ast(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        *,
        parent_node: Optional[qlast.DDLOperation] = None,
    ) -> Optional[qlast.DDLOperation]:
        set_field = super()._get_ast(schema, context, parent_node=parent_node)
        if set_field is None or self.is_attribute_computed('target'):
            return None
        else:
            assert isinstance(set_field, qlast.SetField)
            return qlast.SetPointerType(
                value=set_field.value,
                cast_expr=(
                    self.cast_expr.qlast
                    if self.cast_expr is not None else None
                )
            )