def merge_tensor_chunks(input_tensor, ctx):
    from .executor import Executor
    from .tensor.expressions.fetch import TensorFetch

    if len(input_tensor.chunks) == 1:
        return ctx[input_tensor.chunks[0].key]

    chunks = []
    for c in input_tensor.chunks:
        op = TensorFetch(dtype=c.dtype, sparse=c.op.sparse)
        chunk = op.new_chunk(None, c.shape, index=c.index, _key=c.key)
        chunks.append(chunk)

    new_op = TensorFetch(dtype=input_tensor.dtype, sparse=input_tensor.op.sparse)
    tensor = new_op.new_tensor(None, input_tensor.shape, chunks=chunks,
                               nsplits=input_tensor.nsplits)

    executor = Executor(storage=ctx)
    concat_result = executor.execute_tensor(tensor, concat=True)
    return concat_result[0]