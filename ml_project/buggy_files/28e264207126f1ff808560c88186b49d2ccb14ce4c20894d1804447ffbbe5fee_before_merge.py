    def visit_Attribute(self, n: ast35.Attribute) -> Type:
        before_dot = self.visit(n.value)

        assert isinstance(before_dot, UnboundType)
        assert not before_dot.args

        return UnboundType("{}.{}".format(before_dot.name, n.attr), line=self.line)