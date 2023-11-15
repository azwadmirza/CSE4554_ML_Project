    def execute(cls, ctx, op):
        if len(op.inputs) == 2:
            df, other = ctx[op.inputs[0].key], ctx[op.inputs[1].key]
            if isinstance(op.inputs[0], SERIES_CHUNK_TYPE) and \
                    isinstance(op.inputs[1], DATAFRAME_CHUNK_TYPE):
                df, other = other, df
                func_name = getattr(cls, '_rfunc_name')
            else:
                func_name = getattr(cls, '_func_name')
        elif pd.api.types.is_scalar(op.lhs) or isinstance(op.lhs, np.ndarray):
            df = ctx[op.rhs.key]
            other = op.lhs
            func_name = getattr(cls, '_rfunc_name')
        else:
            df = ctx[op.lhs.key]
            other = op.rhs
            func_name = getattr(cls, '_func_name')
        if df.ndim == 2:
            kw = dict({'axis': op.axis})
        else:
            kw = dict()
        if op.fill_value is not None:
            # comparison function like eq does not have `fill_value`
            kw['fill_value'] = op.fill_value
        if op.level is not None:
            # logical function like and may don't have `level` (for Series type)
            kw['level'] = op.level
        if hasattr(other, 'ndim') and other.ndim == 0:
            other = other.item()
        ctx[op.outputs[0].key] = getattr(df, func_name)(other, **kw)