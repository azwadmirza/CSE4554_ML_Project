    def execute(cls, ctx, op):
        chunk = op.outputs[0]
        if op.input is not None:
            tensor_data = ctx[op.input.key]
        else:
            tensor_data = None
        if op.index is not None:
            index_data = ctx[op.index.key]
        else:
            index_data = chunk.index_value.to_pandas()
        ctx[chunk.key] = pd.Series(tensor_data, index=index_data,
                                   name=chunk.name, dtype=chunk.dtype)