def build_fetch_chunk(chunk, input_chunk_keys=None, **kwargs):
    from .operands import ShuffleProxy

    chunk_op = chunk.op
    params = chunk.params.copy()

    if isinstance(chunk_op, ShuffleProxy):
        # for shuffle nodes, we build FetchShuffle chunks
        # to replace ShuffleProxy
        to_fetch_keys = [pinp.key for pinp in chunk.inputs
                         if input_chunk_keys is None or pinp.key in input_chunk_keys]
        op = get_fetch_op_cls(chunk_op)(to_fetch_keys=to_fetch_keys)
    else:
        # for non-shuffle nodes, we build Fetch chunks
        # to replace original chunk
        op = get_fetch_op_cls(chunk_op)(sparse=chunk.op.sparse)
    return op.new_chunk(None, kws=[params], _key=chunk.key, _id=chunk.id, **kwargs)