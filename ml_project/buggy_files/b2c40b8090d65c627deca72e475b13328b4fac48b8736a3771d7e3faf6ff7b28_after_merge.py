    def _tile_with_tensor(cls, op):
        out = op.outputs[0]
        axis = op.axis
        if axis is None:
            axis = 0

        rhs_is_tensor = isinstance(op.rhs, TENSOR_TYPE)
        tensor, other = (op.rhs, op.lhs) if rhs_is_tensor else (op.lhs, op.rhs)
        if tensor.shape == other.shape:
            tensor = tensor.rechunk(other.nsplits)._inplace_tile()
        else:
            # shape differs only when dataframe add 1-d tensor, we need rechunk on columns axis.
            if axis in ['columns', 1] and other.ndim == 1:
                # force axis == 0 if it's Series other than DataFrame
                axis = 0
            rechunk_size = other.nsplits[1] if axis == 'columns' or axis == 1 else other.nsplits[0]
            if tensor.ndim > 0:
                tensor = tensor.rechunk((rechunk_size,))._inplace_tile()

        cum_splits = [0] + np.cumsum(other.nsplits[axis]).tolist()
        out_chunks = []
        for out_index in itertools.product(*(map(range, other.chunk_shape))):
            tensor_chunk = tensor.cix[out_index[:tensor.ndim]]
            other_chunk = other.cix[out_index]
            out_op = op.copy().reset_key()
            inputs = [other_chunk, tensor_chunk] if rhs_is_tensor else [tensor_chunk, other_chunk]
            if isinstance(other_chunk, DATAFRAME_CHUNK_TYPE):
                start = cum_splits[out_index[axis]]
                end = cum_splits[out_index[axis] + 1]
                chunk_dtypes = out.dtypes.iloc[start: end]
                out_chunk = out_op.new_chunk(inputs, shape=other_chunk.shape, index=other_chunk.index,
                                             dtypes=chunk_dtypes,
                                             index_value=other_chunk.index_value,
                                             columns_value=other.columns_value)
            else:
                out_chunk = out_op.new_chunk(inputs, shape=other_chunk.shape, index=other_chunk.index,
                                             dtype=out.dtype,
                                             index_value=other_chunk.index_value,
                                             name=other_chunk.name)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        if isinstance(other, SERIES_TYPE):
            return new_op.new_seriess(op.inputs, other.shape, nsplits=other.nsplits, dtype=out.dtype,
                                      index_value=other.index_value, chunks=out_chunks)
        else:
            return new_op.new_dataframes(op.inputs, other.shape, nsplits=other.nsplits, dtypes=out.dtypes,
                                         index_value=other.index_value, columns_value=other.columns_value,
                                         chunks=out_chunks)