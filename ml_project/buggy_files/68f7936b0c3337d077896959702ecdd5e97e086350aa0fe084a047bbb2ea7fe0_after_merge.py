    def execute(cls, ctx, op):
        chunk = op.outputs[0]

        if isinstance(op.input, dict):
            d = OrderedDict()
            for k, v in op.input.items():
                if hasattr(v, 'key'):
                    d[k] = ctx[v.key]
                else:
                    d[k] = v
            if op.index is not None:
                index_data = ctx[op.index.key]
            else:
                index_data = chunk.index_value.to_pandas()
            ctx[chunk.key] = pd.DataFrame(d, index=index_data,
                                          columns=chunk.columns_value.to_pandas())
        else:
            tensor_data = ctx[op.inputs[0].key]
            if isinstance(tensor_data, pd.Series):
                ctx[chunk.key] = tensor_data.to_frame(name=chunk.dtypes.index[0])
            else:
                if op.index is not None:
                    # index is a tensor
                    index_data = ctx[op.inputs[1].key]
                else:
                    index_data = chunk.index_value.to_pandas()
                    if isinstance(index_data, pd.RangeIndex) and len(index_data) == 0:
                        index_data = None
                ctx[chunk.key] = pd.DataFrame(tensor_data, index=index_data,
                                              columns=chunk.columns_value.to_pandas())