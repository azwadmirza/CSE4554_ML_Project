    def visit_Subscript(self, n: ast35.Subscript) -> Type:
        if not isinstance(n.slice, ast35.Index):
            self.fail(TYPE_COMMENT_SYNTAX_ERROR, self.line, getattr(n, 'col_offset', -1))
            return AnyType()

        value = self.visit(n.value)

        assert isinstance(value, UnboundType)
        assert not value.args

        empty_tuple_index = False
        if isinstance(n.slice.value, ast35.Tuple):
            params = self.translate_expr_list(n.slice.value.elts)
            if len(n.slice.value.elts) == 0:
                empty_tuple_index = True
        else:
            params = [self.visit(n.slice.value)]

        return UnboundType(value.name, params, line=self.line, empty_tuple_index=empty_tuple_index)