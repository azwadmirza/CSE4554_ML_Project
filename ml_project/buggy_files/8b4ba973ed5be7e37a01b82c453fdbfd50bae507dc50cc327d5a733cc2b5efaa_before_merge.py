    def execute(cls, ctx, op):
        from xgboost import DMatrix

        raw_data = data = ctx[op.data.key]
        if isinstance(data, tuple):
            data = ToDMatrix.get_xgb_dmatrix(data)
        else:
            data = data.spmatrix if hasattr(data, 'spmatrix') else data
            data = DMatrix(data)
        result = op.model.predict(data)

        if isinstance(op.outputs[0], DATAFRAME_CHUNK_TYPE):
            result = pd.DataFrame(result, index=raw_data.index)
        elif isinstance(op.outputs[0], SERIES_CHUNK_TYPE):
            result = pd.Series(result, index=raw_data.index, name='predictions')

        ctx[op.outputs[0].key] = result