    def _tile_offset(cls, op: 'DataFrameReadSQL'):
        df = op.outputs[0]

        if op.row_memory_usage is not None:
            # Data selected
            chunk_size = df.extra_params.raw_chunk_size or options.chunk_size
            if chunk_size is None:
                chunk_size = (int(options.chunk_store_limit / op.row_memory_usage), df.shape[1])
            row_chunk_sizes = normalize_chunk_sizes(df.shape, chunk_size)[0]
        else:
            # No data selected
            row_chunk_sizes = (0,)
        offsets = np.cumsum((0,) + row_chunk_sizes).tolist()

        out_chunks = []
        for i, row_size in enumerate(row_chunk_sizes):
            chunk_op = op.copy().reset_key()
            chunk_op._row_memory_usage = None  # no need for chunk
            offset = chunk_op._offset = offsets[i]
            if df.index_value.has_value():
                # range index
                index_value = parse_index(
                    df.index_value.to_pandas()[offset: offsets[i + 1]])
            else:
                index_value = parse_index(df.index_value.to_pandas(),
                                          op.table_or_sql or str(op.selectable), op.con, i, row_size)
            out_chunk = chunk_op.new_chunk(None, shape=(row_size, df.shape[1]),
                                           columns_value=df.columns_value,
                                           index_value=index_value, dtypes=df.dtypes,
                                           index=(i, 0))
            out_chunks.append(out_chunk)

        nsplits = (row_chunk_sizes, (df.shape[1],))
        new_op = op.copy()
        return new_op.new_dataframes(None, chunks=out_chunks, nsplits=nsplits,
                                     **df.params)