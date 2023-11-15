def pivot(data: "DataFrame", index=None, columns=None, values=None) -> "DataFrame":
    if columns is None:
        raise TypeError("pivot() missing 1 required argument: 'columns'")
    columns = columns if is_list_like(columns) else [columns]

    if values is None:
        cols: List[str] = []
        if index is None:
            pass
        elif is_list_like(index):
            cols = list(index)
        else:
            cols = [index]
        cols.extend(columns)

        append = index is None
        indexed = data.set_index(cols, append=append)
    else:
        if index is None:
            index = [Series(data.index, name=data.index.name)]
        elif is_list_like(index):
            index = [data[idx] for idx in index]
        else:
            index = [data[index]]

        data_columns = [data[col] for col in columns]
        index.extend(data_columns)
        index = MultiIndex.from_arrays(index)

        if is_list_like(values) and not isinstance(values, tuple):
            # Exclude tuple because it is seen as a single column name
            indexed = data._constructor(
                data[values].values, index=index, columns=values
            )
        else:
            indexed = data._constructor_sliced(data[values].values, index=index)
    return indexed.unstack(columns)