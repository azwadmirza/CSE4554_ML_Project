    def _tile_partitioned(cls, op):
        out_df = op.outputs[0]
        shape = (np.nan, out_df.shape[1])
        dtypes = cls._to_arrow_dtypes(out_df.dtypes, op)
        dataset = pq.ParquetDataset(op.path)

        parsed_path = urlparse(op.path)
        if not os.path.exists(op.path) and parsed_path.scheme:
            path_prefix = f'{parsed_path.scheme}://{parsed_path.netloc}'
        else:
            path_prefix = ''

        chunk_index = 0
        out_chunks = []
        for piece in dataset.pieces:
            chunk_op = op.copy().reset_key()
            chunk_op._path = path_prefix + piece.path
            chunk_op._partitions = pickle.dumps(dataset.partitions)
            chunk_op._partition_keys = piece.partition_keys
            new_chunk = chunk_op.new_chunk(
                None, shape=shape, index=(chunk_index, 0),
                index_value=out_df.index_value,
                columns_value=out_df.columns_value,
                dtypes=dtypes)
            out_chunks.append(new_chunk)
            chunk_index += 1

        new_op = op.copy()
        nsplits = ((np.nan,) * len(out_chunks), (out_df.shape[1],))
        return new_op.new_dataframes(None, out_df.shape, dtypes=dtypes,
                                     index_value=out_df.index_value,
                                     columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=nsplits)