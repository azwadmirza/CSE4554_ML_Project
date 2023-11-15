    def visit_forwardref_type(self, t: ForwardRef) -> None:
        self.indicator['forward'] = True
        if t.resolved is None:
            resolved = self.anal_type(t.unbound)
            t.resolve(resolved)