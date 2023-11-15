def db_update(db_path, table, updated_fields, row):
    """ update `table` with the values given in the dict `values` on the
        condition given with the tuple `row`
    """
    field_names = "=?, ".join(updated_fields.keys()) + "=?"
    field_values = tuple(updated_fields.values())
    condition_field = "{0}=?".format(row[0])
    condition_value = (row[1], )
    with db_cursor(db_path) as cursor:
        query = "UPDATE {0} SET {1} WHERE {2}".format(table, field_names,
                                                      condition_field)
        cursor.execute(query, field_values + condition_value)