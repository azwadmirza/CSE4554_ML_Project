    def visit_cast_expr(self, e: CastExpr) -> None:
        self.analyze(e.type, e)
        super().visit_cast_expr(e)