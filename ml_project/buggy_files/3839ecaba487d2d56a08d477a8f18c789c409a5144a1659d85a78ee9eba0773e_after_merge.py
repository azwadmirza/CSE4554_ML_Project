def _copy_expression(expression, source_table, target_table):
    if source_table is None or target_table is None:
        return expression

    def replace(col):
        if (
            isinstance(col, Column)
            and col.table is source_table
            and col.key in source_table.c
        ):
            return target_table.c[col.key]
        else:
            return None

    return visitors.replacement_traverse(expression, {}, replace)