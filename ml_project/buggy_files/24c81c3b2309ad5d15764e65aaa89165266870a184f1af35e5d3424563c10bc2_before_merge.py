    def tile(cls, op):
        if op.compression:
            return cls._tile_compressed(op)

        df = op.outputs[0]
        chunk_bytes = df.extra_params.chunk_bytes
        chunk_bytes = int(parse_readable_size(chunk_bytes)[0])

        dtypes = df.dtypes
        if op.use_arrow_dtype is None and not op.gpu and \
                options.dataframe.use_arrow_dtype:  # pragma: no cover
            # check if use_arrow_dtype set on the server side
            dtypes = to_arrow_dtypes(df.dtypes)

        paths = op.path if isinstance(op.path, (tuple, list)) else glob(op.path, storage_options=op.storage_options)

        out_chunks = []
        index_num = 0
        for path in paths:
            total_bytes = file_size(path)
            offset = 0
            for _ in range(int(np.ceil(total_bytes * 1.0 / chunk_bytes))):
                chunk_op = op.copy().reset_key()
                chunk_op._path = path
                chunk_op._offset = offset
                chunk_op._size = min(chunk_bytes, total_bytes - offset)
                shape = (np.nan, len(dtypes))
                index_value = parse_index(df.index_value.to_pandas(), path, index_num)
                new_chunk = chunk_op.new_chunk(None, shape=shape, index=(index_num, 0), index_value=index_value,
                                               columns_value=df.columns_value, dtypes=dtypes)
                out_chunks.append(new_chunk)
                index_num += 1
                offset += chunk_bytes

        if op.incremental_index and len(out_chunks) > 1 and \
                isinstance(df.index_value._index_value, IndexValue.RangeIndex):
            out_chunks = standardize_range_index(out_chunks)
        new_op = op.copy()
        nsplits = ((np.nan,) * len(out_chunks), (df.shape[1],))
        return new_op.new_dataframes(None, df.shape, dtypes=dtypes,
                                     index_value=df.index_value,
                                     columns_value=df.columns_value,
                                     chunks=out_chunks, nsplits=nsplits)