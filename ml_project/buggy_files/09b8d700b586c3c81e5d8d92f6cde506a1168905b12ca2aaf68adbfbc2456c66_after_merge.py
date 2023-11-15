    def visit_func_def(self, fdef: FuncDef) -> None:
        self.errors.push_function(fdef.name())
        self.analyze(fdef.type, fdef)
        super().visit_func_def(fdef)
        self.errors.pop_function()