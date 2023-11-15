    def copy(self, target_table=None, **kw):
        elements = [
            (
                schema._copy_expression(expr, self.parent, target_table),
                self.operators[expr.name],
            )
            for expr in self.columns
        ]
        c = self.__class__(
            *elements,
            name=self.name,
            deferrable=self.deferrable,
            initially=self.initially,
            where=self.where,
            using=self.using
        )
        c.dispatch._update(self.dispatch)
        return c