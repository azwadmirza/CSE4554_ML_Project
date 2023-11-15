    def copy(self, target_table=None, **kw):
        sqltext = _copy_expression(
            self.sqltext,
            self.column.table if self.column is not None else None,
            target_table,
        )
        g = Computed(sqltext, persisted=self.persisted)

        return self._schema_item_copy(g)