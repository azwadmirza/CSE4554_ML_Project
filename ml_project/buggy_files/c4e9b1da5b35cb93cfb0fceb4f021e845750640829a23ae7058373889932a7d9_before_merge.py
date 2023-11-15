    def tile(cls, op):
        df = op.outputs[0]
        tensor = op.inputs[0]

        nsplit_acc = np.cumsum(tensor.nsplits[0])
        out_chunks = []
        for chunk in tensor.chunks:
            begin_index = nsplit_acc[chunk.index[0]] - chunk.shape[0]
            end_index = nsplit_acc[chunk.index[0]]
            chunk_index_value = parse_index(pd.RangeIndex(start=begin_index, stop=end_index))

            # Here the `new_chunk` is tricky:
            #
            # We can construct tensor that have identifcal chunks, for example, from `mt.ones(...)`, we know
            # that after tiling the chunk of the same shape (but at different position) in `mt.ones` is indeed
            # the same chunk (has the same key)!
            #
            # Thus, when we construct dataframe from such tensor, we will have dataframe chunks that only differ
            # in `index_value`. However the `index_value` field won't be used to calculate the chunk key of
            # the dataframe chunk, thus `new_chunk` generated the same keys for those indeed different chunks
            # (they have different `index_values`).
            #
            # Here, we construct new chunk with some unique `_extra_params` to make the `new_chunk` work as
            # expected.
            chunk_op = op.copy().reset_key()
            chunk_op.extra_params['begin_index'] = begin_index
            chunk_op.extra_params['end_index'] = end_index
            out_chunk = chunk_op.new_chunk(
                [chunk], shape=(chunk.shape[0], df.shape[1]), index=(chunk.index[0], 0), dtypes=df.dtypes,
                index_value=chunk_index_value, columns_value=df.columns)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes([tensor], df.shape, dtypes=df.dtypes,
                                     index_value=df.index_value,
                                     columns_value=df.columns,
                                     chunks=out_chunks, nsplits=[tensor.nsplits[0], [df.shape[1]]])