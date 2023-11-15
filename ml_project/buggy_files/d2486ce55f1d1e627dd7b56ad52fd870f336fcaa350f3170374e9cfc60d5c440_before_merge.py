    def _infer_expr(self, expr):
        # Infer an expression: handle supported cases
        if expr.op == 'call':
            func = self.infer_constant(expr.func.name)
            return self._infer_call(func, expr)
        elif expr.op == 'getattr':
            value = self.infer_constant(expr.value.name)
            return self._infer_getattr(value, expr)
        elif expr.op == 'build_list':
            return [self.infer_constant(i.name) for i in expr.items]
        elif expr.op == 'build_tuple':
            return tuple(self.infer_constant(i.name) for i in expr.items)
        self._fail(expr)