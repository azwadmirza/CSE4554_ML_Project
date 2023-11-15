    def visit_set_expr(self, expr: SetExpr) -> None:
        for item in expr.items:
            item.accept(self)