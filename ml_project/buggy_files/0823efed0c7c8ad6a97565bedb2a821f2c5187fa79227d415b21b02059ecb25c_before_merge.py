    def _execute_combine(cls, ctx, op):
        xdf = cudf if op.gpu else pd
        in_data = ctx[op.inputs[0].key]
        count_sum = in_data.sum(axis=op.axis)
        if isinstance(in_data, xdf.Series):
            ctx[op.outputs[0].key] = count_sum
        else:
            ctx[op.outputs[0].key] = xdf.DataFrame(count_sum) if op.axis == 1 else xdf.DataFrame(count_sum).transpose()