    def visit_forwardref_type(self, t: ForwardRef) -> None:
        self.indicator['forward'] = True
        if t.resolved is None:
            resolved = self.anal_type(t.unbound)
            t.resolve(resolved)
            assert t.resolved is not None
            t.resolved.accept(self)