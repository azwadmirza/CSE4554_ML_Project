    def execute(cls, ctx, op):
        chunk = op.outputs[0]
        ctx[chunk.key] = pd.DataFrame.from_records(
            ctx[op.inputs[0].key],
            index=chunk.index_value.to_pandas(), columns=chunk.columns.to_pandas(),
            exclude=op.exclude, coerce_float=op.coerce_float, nrows=op.nrows)