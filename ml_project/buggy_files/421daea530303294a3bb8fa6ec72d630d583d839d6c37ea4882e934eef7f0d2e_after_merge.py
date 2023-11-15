    def visit_For(self, node):
        """Handle visiting a for statement."""
        targ = node.target
        self.ctxupdate(gather_names(targ))
        self.generic_visit(node)
        return node