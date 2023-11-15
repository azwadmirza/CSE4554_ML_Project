    def visit_star_expr(self, expr: StarExpr) -> None:
        if not expr.valid:
            self.fail('Can use starred expression only as assignment target', expr)
        else:
            expr.expr.accept(self)