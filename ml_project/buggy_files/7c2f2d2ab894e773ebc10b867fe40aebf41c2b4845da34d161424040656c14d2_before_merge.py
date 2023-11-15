    def copy(self, target_table=None, **kw):
        if target_table is not None:
            sqltext = _copy_expression(self.sqltext, self.table, target_table)
        else:
            sqltext = self.sqltext
        c = CheckConstraint(
            sqltext,
            name=self.name,
            initially=self.initially,
            deferrable=self.deferrable,
            _create_rule=self._create_rule,
            table=target_table,
            _autoattach=False,
            _type_bound=self._type_bound,
        )
        return self._schema_item_copy(c)