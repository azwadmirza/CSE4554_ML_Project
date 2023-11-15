    def visit_on_duplicate_key_update(self, on_duplicate, **kw):
        if on_duplicate._parameter_ordering:
            parameter_ordering = [
                elements._column_as_key(key)
                for key in on_duplicate._parameter_ordering
            ]
            ordered_keys = set(parameter_ordering)
            cols = [
                self.statement.table.c[key]
                for key in parameter_ordering
                if key in self.statement.table.c
            ] + [
                c for c in self.statement.table.c if c.key not in ordered_keys
            ]
        else:
            cols = self.statement.table.c

        clauses = []
        # traverses through all table columns to preserve table column order
        for column in (col for col in cols if col.key in on_duplicate.update):

            val = on_duplicate.update[column.key]

            if elements._is_literal(val):
                val = elements.BindParameter(None, val, type_=column.type)
                value_text = self.process(val.self_group(), use_schema=False)
            else:

                def replace(obj):
                    if (
                        isinstance(obj, elements.BindParameter)
                        and obj.type._isnull
                    ):
                        obj = obj._clone()
                        obj.type = column.type
                        return obj
                    elif (
                        isinstance(obj, elements.ColumnClause)
                        and obj.table is on_duplicate.inserted_alias
                    ):
                        obj = literal_column(
                            "VALUES(" + self.preparer.quote(column.name) + ")"
                        )
                        return obj
                    else:
                        # element is not replaced
                        return None

                val = visitors.replacement_traverse(val, {}, replace)
                value_text = self.process(val.self_group(), use_schema=False)

            name_text = self.preparer.quote(column.name)
            clauses.append("%s = %s" % (name_text, value_text))

        non_matching = set(on_duplicate.update) - set(c.key for c in cols)
        if non_matching:
            util.warn(
                "Additional column names not matching "
                "any column keys in table '%s': %s"
                % (
                    self.statement.table.name,
                    (", ".join("'%s'" % c for c in non_matching)),
                )
            )

        return "ON DUPLICATE KEY UPDATE " + ", ".join(clauses)