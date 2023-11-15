    def op_RAISE_VARARGS(self, inst, exc):
        if exc is not None:
            exc = self.get(exc)
        stmt = ir.Raise(exception=exc, loc=self.loc)
        self.current_block.append(stmt)