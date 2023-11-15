    def copy(self, **kw):
        elements = [(col, self.operators[col]) for col in self.columns.keys()]
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