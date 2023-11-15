def arrow_table_to_pandas_dataframe(arrow_table, use_arrow_dtype=True, **kw):
    if not use_arrow_dtype:
        # if not use arrow string, just return
        return arrow_table.to_pandas(**kw)

    from .arrays import ArrowStringArray

    table: pa.Table = arrow_table
    schema: pa.Schema = arrow_table.schema

    string_field_names = list()
    string_arrays = list()
    string_indexes = list()
    other_field_names = list()
    other_arrays = list()
    for i, arrow_type in enumerate(schema.types):
        if arrow_type == pa.string():
            string_field_names.append(schema.names[i])
            string_indexes.append(i)
            string_arrays.append(table.columns[i])
        else:
            other_field_names.append(schema.names[i])
            other_arrays.append(table.columns[i])

    df: pd.DataFrame = pa.Table.from_arrays(
        other_arrays, names=other_field_names).to_pandas(**kw)
    for string_index, string_name, string_array in \
            zip(string_indexes, string_field_names, string_arrays):
        df.insert(string_index, string_name,
                  pd.Series(ArrowStringArray(string_array)))

    return df