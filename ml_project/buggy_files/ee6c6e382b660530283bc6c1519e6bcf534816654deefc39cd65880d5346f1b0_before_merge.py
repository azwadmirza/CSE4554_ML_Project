    def _add_select(self, table_set):
        to_select = []
        for expr in self.select_set:
            if isinstance(expr, ir.ValueExpr):
                arg = self._translate(expr, named=True)
            elif isinstance(expr, ir.TableExpr):
                if expr.equals(self.table_set):
                    cached_table = self.context.get_table(expr)
                    if cached_table is None:
                        # the select * case from materialized join
                        arg = '*'
                    else:
                        arg = table_set
                else:
                    arg = self.context.get_table(expr)
                    if arg is None:
                        raise ValueError(expr)

            to_select.append(arg)

        if self.exists:
            clause = sa.exists(to_select)
        else:
            clause = sa.select(to_select)

        if self.distinct:
            clause = clause.distinct()

        if table_set is not None:
            return clause.select_from(table_set)
        else:
            return clause