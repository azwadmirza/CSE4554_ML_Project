    def tile(cls, op):
        df = op.outputs[0]
        raw_df = op.data

        memory_usage = raw_df.memory_usage(index=False, deep=True)
        chunk_size = df.extra_params.raw_chunk_size or options.tensor.chunk_size
        chunk_size = decide_dataframe_chunk_sizes(df.shape, chunk_size, memory_usage)
        chunk_size_idxes = (range(len(size)) for size in chunk_size)

        out_chunks = []
        for chunk_shape, chunk_idx in izip(itertools.product(*chunk_size),
                                           itertools.product(*chunk_size_idxes)):
            chunk_op = op.copy().reset_key()
            slc = get_chunk_slices(chunk_size, chunk_idx)
            chunk_op._data = raw_df.iloc[slc]
            chunk_op._dtypes = chunk_op._data.dtypes
            out_chunk = chunk_op.new_chunk(None, shape=chunk_shape, index=chunk_idx,
                                           index_value=parse_index(chunk_op.data.index),
                                           columns_value=parse_index(chunk_op.data.columns,
                                                                     store_data=True),
                                           dtypes=chunk_op._data.dtypes)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(None, df.shape, dtypes=op.dtypes,
                                     index_value=df.index_value,
                                     columns_value=df.columns,
                                     chunks=out_chunks, nsplits=chunk_size)