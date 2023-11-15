    def visit_set_expr(self, e: SetExpr) -> Type:
        return self.check_list_or_set_expr(e.items, 'builtins.set', '<set>', e)