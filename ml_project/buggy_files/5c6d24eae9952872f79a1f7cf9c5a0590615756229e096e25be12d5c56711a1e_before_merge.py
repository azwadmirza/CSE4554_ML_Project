    def _set_parent(self, table):
        for col in self._pending_colargs:
            if isinstance(col, util.string_types):
                col = table.c[col]
            self.columns.add(col)