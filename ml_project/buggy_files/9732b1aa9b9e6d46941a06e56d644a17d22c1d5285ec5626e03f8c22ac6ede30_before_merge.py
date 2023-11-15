    def execute(cls, ctx, op):
        chunk = op.outputs[0]
        tensor_data = ctx[op.inputs[0].key]
        if op.index is not None:
            index_data = ctx[op.inputs[1].key]
        else:
            index_data = chunk.index_value.to_pandas()
        ctx[chunk.key] = pd.Series(tensor_data, index=index_data, name=chunk.name)