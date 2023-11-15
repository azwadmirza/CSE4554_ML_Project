    def execute(cls, ctx, op):
        if op.mask is None:
            df = ctx[op.inputs[0].key]
            ctx[op.outputs[0].key] = df[op.col_names]
        else:
            df = ctx[op.inputs[0].key]
            if isinstance(op.mask, (SERIES_CHUNK_TYPE, DATAFRAME_CHUNK_TYPE,
                                    TENSOR_CHUNK_TYPE)):
                mask = ctx[op.inputs[1].key]
            else:
                mask = op.mask
            if hasattr(mask, 'reindex_like'):
                mask = mask.reindex_like(df).fillna(False)
            if mask.ndim == 2:
                mask = mask[df.columns.tolist()]
            ctx[op.outputs[0].key] = df[mask]