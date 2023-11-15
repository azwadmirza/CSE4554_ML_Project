    def visit_yield_expr(self, expr: YieldExpr) -> None:
        if not self.is_func_scope():
            self.fail("'yield' outside function", expr, True, blocker=True)
        else:
            self.function_stack[-1].is_generator = True
        if expr.expr:
            expr.expr.accept(self)