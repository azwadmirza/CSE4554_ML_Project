    def visit_yield_from_expr(self, e: YieldFromExpr) -> None:
        if not self.is_func_scope():  # not sure
            self.fail("'yield from' outside function", e, True, blocker=True)
        else:
            self.function_stack[-1].is_generator = True
        if e.expr:
            e.expr.accept(self)