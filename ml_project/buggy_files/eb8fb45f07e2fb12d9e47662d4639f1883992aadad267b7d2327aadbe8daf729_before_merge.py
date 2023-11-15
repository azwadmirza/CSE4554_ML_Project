    def visit_list_expr(self, e: ListExpr) -> Type:
        """Type check a list expression [...]."""
        return self.check_list_or_set_expr(e.items, 'builtins.list', '<list>',
                                           e)