    def visit_Attribute(self, n: ast35.Attribute) -> Type:
        before_dot = self.visit(n.value)

        if isinstance(before_dot, UnboundType) and not before_dot.args:
            return UnboundType("{}.{}".format(before_dot.name, n.attr), line=self.line)
        else:
            self.fail(TYPE_COMMENT_AST_ERROR, self.line, getattr(n, 'col_offset', -1))
            return AnyType()