    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        for item in expr.items:
            item.accept(self)