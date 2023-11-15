def _index_set_value(ctx, chunk):
    indexes = [ctx[index.key] if hasattr(index, 'key') else index
               for index in chunk.op.indexes]
    input = ctx[chunk.inputs[0].key].copy()
    value = ctx[chunk.op.value.key] if hasattr(chunk.op.value, 'key') else chunk.op.value
    if hasattr(input, 'flags') and not input.flags.writeable:
        input.setflags(write=True)
    input[tuple(indexes)] = value
    ctx[chunk.key] = input