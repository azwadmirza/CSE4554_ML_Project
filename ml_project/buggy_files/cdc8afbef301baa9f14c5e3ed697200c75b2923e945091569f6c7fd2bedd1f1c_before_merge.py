def table_from_data(data, column_names):
    "Convert list of dictionaries into an Agate table"

    # The agate table is generated from a list of dicts, so the column order
    # from `data` is not preserved. We can use `select` to reorder the columns
    #
    # If there is no data, create an empty table with the specified columns

    if len(data) == 0:
        return agate.Table([], column_names=column_names)
    else:
        table = agate.Table.from_object(data, column_types=DEFAULT_TYPE_TESTER)
        return table.select(column_names)