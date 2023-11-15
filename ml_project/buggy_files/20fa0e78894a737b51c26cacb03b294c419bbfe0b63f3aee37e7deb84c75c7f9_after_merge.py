def table_from_data_flat(data, column_names: Iterable[str]) -> agate.Table:
    "Convert list of dictionaries into an Agate table"

    rows = []
    for _row in data:
        row = []
        for value in list(_row.values()):
            if isinstance(value, (dict, list, tuple)):
                row.append(json.dumps(value))
            else:
                row.append(value)
        rows.append(row)

    return table_from_rows(rows=rows, column_names=column_names)