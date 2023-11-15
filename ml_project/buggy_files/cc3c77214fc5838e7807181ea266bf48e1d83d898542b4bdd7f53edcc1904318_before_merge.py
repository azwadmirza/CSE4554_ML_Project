    def copy(self, target_table=None, **kw):
        if target_table is not None:
            sqltext = _copy_expression(self.sqltext, self.table, target_table)
        else:
            sqltext = self.sqltext
        g = Computed(sqltext, persisted=self.persisted)

        return self._schema_item_copy(g)