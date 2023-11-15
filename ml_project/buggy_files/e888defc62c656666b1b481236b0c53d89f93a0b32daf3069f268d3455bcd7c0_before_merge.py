    def apply(self):
        """
        Rewrite all matching getitems as static_getitems.
        """
        for expr, const in self.getitems:
            expr.op = 'static_getitem'
            expr.index_var = expr.index
            expr.index = const
        return self.block