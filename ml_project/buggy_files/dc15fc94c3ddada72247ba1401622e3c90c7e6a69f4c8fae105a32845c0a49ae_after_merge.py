def standardize_range_index(chunks, axis=0):
    from .base.standardize_range_index import ChunkStandardizeRangeIndex

    row_chunks = dict((k, next(v)) for k, v in itertools.groupby(chunks, key=lambda x: x.index[axis]))
    row_chunks = [row_chunks[i] for i in range(len(row_chunks))]

    out_chunks = []
    for c in chunks:
        inputs = row_chunks[:c.index[axis]] + [c]
        op = ChunkStandardizeRangeIndex(
            prepare_inputs=[False] * (len(inputs) - 1) + [True], axis=axis, output_types=c.op.output_types)
        out_chunks.append(op.new_chunk(inputs, **c.params.copy()))

    return out_chunks