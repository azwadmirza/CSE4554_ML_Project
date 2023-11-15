def _constraint_name(const, table):
    if isinstance(table, Column):
        # for column-attached constraint, set another event
        # to link the column attached to the table as this constraint
        # associated with the table.
        event.listen(
            table,
            "after_parent_attach",
            lambda col, table: _constraint_name(const, table),
        )
    elif isinstance(table, Table):
        if isinstance(const.name, (conv, _defer_name)):
            return

        newname = _constraint_name_for_table(const, table)
        if newname is not None:
            const.name = newname