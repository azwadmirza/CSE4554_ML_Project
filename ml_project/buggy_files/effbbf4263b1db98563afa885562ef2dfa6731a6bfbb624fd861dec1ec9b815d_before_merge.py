    def execute(cls, ctx, op: "DataFrameValueCounts"):
        if op.stage != OperandStage.map:
            in_data = ctx[op.input.key]
            if op.convert_index_to_interval:
                result = in_data.value_counts(
                    normalize=False, sort=op.sort, ascending=op.ascending,
                    bins=op.bins, dropna=op.dropna)
                if op.normalize:
                    result /= in_data.shape[0]
            else:
                try:
                    result = in_data.value_counts(
                        normalize=op.normalize, sort=op.sort, ascending=op.ascending,
                        bins=op.bins, dropna=op.dropna)
                except ValueError:
                    in_data = in_data.copy()
                    result = in_data.value_counts(
                        normalize=op.normalize, sort=op.sort, ascending=op.ascending,
                        bins=op.bins, dropna=op.dropna)
        else:
            result = ctx[op.input.key]
        if op.convert_index_to_interval:
            # convert CategoricalDtype which generated in `cut`
            # to IntervalDtype
            result.index = result.index.astype('interval')
        ctx[op.outputs[0].key] = result