    def _set_parent(self, table):
        for col in self._col_expressions(table):
            if col is not None:
                self.columns.add(col)