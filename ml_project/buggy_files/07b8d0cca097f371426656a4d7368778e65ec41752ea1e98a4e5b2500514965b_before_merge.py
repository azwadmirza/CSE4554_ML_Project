    def execute(cls, ctx, op):
        chunk = op.outputs[0]
        tensor_data = ctx[op.inputs[0].key]
        ctx[chunk.key] = pd.DataFrame(tensor_data, index=chunk.index_value.to_pandas(),
                                      columns=chunk.columns.to_pandas())