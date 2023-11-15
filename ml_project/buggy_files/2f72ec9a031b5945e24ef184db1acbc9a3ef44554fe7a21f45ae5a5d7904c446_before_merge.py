    def visit_list_expr(self, expr: ListExpr) -> None:
        for item in expr.items:
            item.accept(self)