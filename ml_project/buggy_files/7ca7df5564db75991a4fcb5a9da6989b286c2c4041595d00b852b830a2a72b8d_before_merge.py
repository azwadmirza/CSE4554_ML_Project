def build_concated_rows_frame(df):
    from .operands import ObjectType
    from .merge.concat import DataFrameConcat

    # When the df isn't splitted along the column axis, return the df directly.
    if df.chunk_shape[1] == 1:
        return df

    columns = concat_index_value([df.cix[0, idx].columns for idx in range(df.chunk_shape[1])],
                                 store_data=True)
    columns_size = columns.to_pandas().size

    out_chunks = []
    for idx in range(df.chunk_shape[0]):
        out_chunk = DataFrameConcat(axis=1, object_type=ObjectType.dataframe).new_chunk(
            [df.cix[idx, k] for k in range(df.chunk_shape[1])], index=(idx, 0),
            shape=(df.cix[idx, 0].shape[0], columns_size), dtypes=df.dtypes,
            index_value=df.cix[idx, 0].index_value, columns_value=columns)
        out_chunks.append(out_chunk)

    return DataFrameConcat(axis=1, object_type=ObjectType.dataframe).new_dataframe(
        [df], chunks=out_chunks, nsplits=((chunk.shape[0] for chunk in out_chunks), (df.shape[1],)),
        shape=df.shape, dtypes=df.dtypes,
        index_value=df.index_value, columns_value=df.columns)