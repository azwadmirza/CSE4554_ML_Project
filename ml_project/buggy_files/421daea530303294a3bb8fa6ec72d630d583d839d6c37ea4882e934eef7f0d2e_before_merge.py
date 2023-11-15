    def visit_For(self, node):
        """Handle visiting a for statement."""
        targ = node.target
        if isinstance(targ, (Tuple, List)):
            self.ctxupdate(leftmostname(elt) for elt in targ.elts)
        else:
            self.ctxadd(leftmostname(targ))
        self.generic_visit(node)
        return node