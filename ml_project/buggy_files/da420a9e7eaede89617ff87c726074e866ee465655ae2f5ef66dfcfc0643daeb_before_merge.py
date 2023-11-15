def ensure_not_chunked(arrow_array):
    if isinstance(arrow_array, pa.ChunkedArray):
        if len(arrow_array.chunks) == 0:
            return arrow_array.chunks[0]
        table = pa.Table.from_arrays([arrow_array], ["single"])
        table_concat = table.combine_chunks()
        column = table_concat.columns[0]
        assert column.num_chunks == 1
        arrow_array = column.chunk(0)
    return arrow_array