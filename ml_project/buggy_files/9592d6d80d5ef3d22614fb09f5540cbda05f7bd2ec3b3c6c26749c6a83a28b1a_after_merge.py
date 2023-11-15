    def _execute_without_count(cls, ctx, op, reduction_func=None):
        # Execution for normal reduction operands.

        # For dataframe, will keep dimensions for intermediate results.
        xdf = cudf if op.gpu else pd
        in_data = ctx[op.inputs[0].key]
        r = cls._execute_reduction(in_data, op, min_count=op.min_count, reduction_func=reduction_func)
        if isinstance(in_data, xdf.Series) or op.output_types[0] == OutputType.series:
            ctx[op.outputs[0].key] = r
        else:
            if op.axis == 0:
                if op.gpu:
                    df = xdf.DataFrame(r).transpose()
                    df.columns = r.index.to_arrow().to_pylist()
                else:
                    # cannot just do xdf.DataFrame(r).T
                    # cuz the dtype will be object since pandas 1.0
                    df = xdf.DataFrame(OrderedDict((d, [v]) for d, v in r.iteritems()))
            else:
                df = xdf.DataFrame(r)
            ctx[op.outputs[0].key] = df