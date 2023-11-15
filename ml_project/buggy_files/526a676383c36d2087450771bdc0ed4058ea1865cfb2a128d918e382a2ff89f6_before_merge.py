    def _gen_shuffle_chunks(cls, op, out_shape, shuffle_on, df):
        # gen map chunks
        map_chunks = []
        for chunk in df.chunks:
            map_op = DataFrameMergeAlignMap(shuffle_on=shuffle_on,
                                            sparse=chunk.issparse(),
                                            index_shuffle_size=out_shape[0])
            map_chunks.append(map_op.new_chunk([chunk], shape=(np.nan, np.nan), dtypes=chunk.dtypes, index=chunk.index,
                                               index_value=chunk.index_value, columns_value=chunk.columns))

        proxy_chunk = DataFrameShuffleProxy(object_type=ObjectType.dataframe).new_chunk(
            map_chunks, shape=(), dtypes=df.dtypes,
            index_value=df.index_value, columns_value=df.columns)

        # gen reduce chunks
        reduce_chunks = []
        for out_idx in itertools.product(*(range(s) for s in out_shape)):
            reduce_op = DataFrameMergeAlignReduce(sparse=proxy_chunk.issparse(),
                                                  shuffle_key=','.join(str(idx) for idx in out_idx))
            reduce_chunks.append(
                reduce_op.new_chunk([proxy_chunk], shape=(np.nan, np.nan), dtypes=proxy_chunk.dtypes, index=out_idx,
                                    index_value=proxy_chunk.index_value, columns_value=proxy_chunk.columns))
        return reduce_chunks