    def execute(cls, ctx, op):
        chunk = op.outputs[0]

        if op.from_1d_tensors:
            d = OrderedDict()
            tensors = [ctx[inp.key] for inp in op.inputs]
            if op.index is not None:
                tensors_data, index_data = tensors[:-1], tensors[-1]
            else:
                tensors_data = tensors
                index_data = chunk.index_value.to_pandas()
            for name, data_1d in zip(chunk.dtypes.index, tensors_data):
                d[name] = data_1d
            ctx[chunk.key] = pd.DataFrame(d, index=index_data,
                                          columns=chunk.columns_value.to_pandas())
        else:
            tensor_data = ctx[op.inputs[0].key]
            if op.index is not None:
                # index is a tensor
                index_data = ctx[op.inputs[1].key]
            else:
                index_data = chunk.index_value.to_pandas()
            ctx[chunk.key] = pd.DataFrame(tensor_data, index=index_data,
                                          columns=chunk.columns_value.to_pandas())