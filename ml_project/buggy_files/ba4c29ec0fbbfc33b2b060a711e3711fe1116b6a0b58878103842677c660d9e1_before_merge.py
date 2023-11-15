    def _fill_empty(self, declaration, docname):
        # type: (ASTDeclaration, unicode) -> None
        self._assert_invariants()
        assert not self.declaration
        assert not self.docname
        assert declaration
        assert docname
        self.declaration = declaration
        self.declaration.symbol = self
        self.docname = docname
        self._assert_invariants()