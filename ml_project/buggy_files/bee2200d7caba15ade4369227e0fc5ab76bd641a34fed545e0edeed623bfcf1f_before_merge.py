def db_insert(db_path, table, fields):
    field_names = ", ".join(fields.keys())
    placeholders = ("?, " * len(fields))[:-2]
    field_values = tuple(fields.values())
    with db_cursor(db_path) as cursor:
        cursor.execute(
            "insert into {0}({1}) values ({2})".format(table,
                                                       field_names,
                                                       placeholders),
            field_values
        )