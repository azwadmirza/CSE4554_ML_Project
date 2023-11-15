    def _set_parent(self, table):
        ColumnCollectionMixin._set_parent(self, table)

        if self.table is not None and table is not self.table:
            raise exc.ArgumentError(
                "Index '%s' is against table '%s', and "
                "cannot be associated with table '%s'."
                % (self.name, self.table.description, table.description)
            )
        self.table = table
        table.indexes.add(self)

        expressions = self.expressions
        col_expressions = self._col_expressions(table)
        assert len(expressions) == len(col_expressions)
        self.expressions = [
            expr if isinstance(expr, ClauseElement) else colexpr
            for expr, colexpr in zip(expressions, col_expressions)
        ]