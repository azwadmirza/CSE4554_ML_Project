    def tile(cls, op):
        out = op.outputs[0]
        target = op.target
        value = op.value
        col = op.indexes
        columns = target.columns_value.to_pandas()

        if not np.isscalar(value):
            # check if all chunk's index_value are identical
            target_chunk_index_values = [c.index_value for c in target.chunks
                                         if c.index[1] == 0]
            value_chunk_index_values = [v.index_value for v in value.chunks]
            is_identical = len(target_chunk_index_values) == len(target_chunk_index_values) and \
                all(c.key == v.key for c, v in zip(target_chunk_index_values, value_chunk_index_values))
            if not is_identical:
                # do rechunk
                if any(np.isnan(s) for s in target.nsplits[0]) or \
                        any(np.isnan(s) for s in value.nsplits[0]):  # pragma: no cover
                    raise TilesError('target or value has unknown chunk shape')

                value = value.rechunk({0: target.nsplits[0]})._inplace_tile()

        out_chunks = []
        nsplits = [list(ns) for ns in target.nsplits]
        if col not in columns:
            nsplits[1][-1] += 1
            column_chunk_shape = target.chunk_shape[1]
            # append to the last chunk on columns axis direction
            for c in target.chunks:
                if c.index[-1] != column_chunk_shape - 1:
                    # not effected, just output
                    out_chunks.append(c)
                else:
                    chunk_op = op.copy().reset_key()
                    if np.isscalar(value):
                        chunk_inputs = [c]
                    else:
                        value_chunk = value.cix[c.index[0], ]
                        chunk_inputs = [c, value_chunk]

                    dtypes = c.dtypes.copy(deep=True)
                    dtypes.loc[out.dtypes.index[-1]] = out.dtypes.iloc[-1]
                    chunk = chunk_op.new_chunk(chunk_inputs,
                                               shape=(c.shape[0], c.shape[1] + 1),
                                               dtypes=dtypes,
                                               index_value=c.index_value,
                                               columns_value=parse_index(dtypes.index, store_data=True),
                                               index=c.index)
                    out_chunks.append(chunk)
        else:
            # replace exist column
            for c in target.chunks:
                if col in c.dtypes:
                    chunk_inputs = [c]
                    if not np.isscalar(value):
                        chunk_inputs.append(value.cix[c.index[0], ])
                    chunk_op = op.copy().reset_key()
                    chunk = chunk_op.new_chunk(chunk_inputs,
                                               shape=c.shape,
                                               dtypes=c.dtypes,
                                               index_value=c.index_value,
                                               columns_value=c.columns_value,
                                               index=c.index)
                    out_chunks.append(chunk)
                else:
                    out_chunks.append(c)

        params = out.params
        params['nsplits'] = tuple(tuple(ns) for ns in nsplits)
        params['chunks'] = out_chunks
        new_op = op.copy()
        return new_op.new_tileables(op.inputs, kws=[params])