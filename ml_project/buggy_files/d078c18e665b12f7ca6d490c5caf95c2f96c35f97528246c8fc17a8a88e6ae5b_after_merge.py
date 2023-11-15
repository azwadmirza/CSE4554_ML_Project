    def visit_on_conflict_do_update(self, on_conflict, **kw):

        clause = on_conflict

        target_text = self._on_conflict_target(on_conflict, **kw)

        action_set_ops = []

        set_parameters = dict(clause.update_values_to_set)
        # create a list of column assignment clauses as tuples

        insert_statement = self.stack[-1]["selectable"]
        cols = insert_statement.table.c
        for c in cols:
            col_key = c.key
            if col_key in set_parameters:
                value = set_parameters.pop(col_key)
                if coercions._is_literal(value):
                    value = elements.BindParameter(None, value, type_=c.type)

                else:
                    if (
                        isinstance(value, elements.BindParameter)
                        and value.type._isnull
                    ):
                        value = value._clone()
                        value.type = c.type
                value_text = self.process(value.self_group(), use_schema=False)

                key_text = self.preparer.quote(col_key)
                action_set_ops.append("%s = %s" % (key_text, value_text))

        # check for names that don't match columns
        if set_parameters:
            util.warn(
                "Additional column names not matching "
                "any column keys in table '%s': %s"
                % (
                    self.current_executable.table.name,
                    (", ".join("'%s'" % c for c in set_parameters)),
                )
            )
            for k, v in set_parameters.items():
                key_text = (
                    self.preparer.quote(k)
                    if isinstance(k, util.string_types)
                    else self.process(k, use_schema=False)
                )
                value_text = self.process(
                    coercions.expect(roles.ExpressionElementRole, v),
                    use_schema=False,
                )
                action_set_ops.append("%s = %s" % (key_text, value_text))

        action_text = ", ".join(action_set_ops)
        if clause.update_whereclause is not None:
            action_text += " WHERE %s" % self.process(
                clause.update_whereclause, include_table=True, use_schema=False
            )

        return "ON CONFLICT %s DO UPDATE SET %s" % (target_text, action_text)