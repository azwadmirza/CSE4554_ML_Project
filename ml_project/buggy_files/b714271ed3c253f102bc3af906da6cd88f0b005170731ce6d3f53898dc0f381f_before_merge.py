def arrow_array_to_objects(obj):
    from .dataframe.arrays import ArrowDtype

    if isinstance(obj, pd.DataFrame):
        out_cols = dict()
        for col_name, dtype in obj.dtypes.items():
            if isinstance(dtype, ArrowDtype):
                out_cols[col_name] = pd.Series(obj[col_name].to_numpy(), index=obj.index)
            else:
                out_cols[col_name] = obj[col_name]
        obj = pd.DataFrame(out_cols, columns=list(obj.dtypes.keys()))
    elif isinstance(obj, pd.Series):
        if isinstance(obj.dtype, ArrowDtype):
            obj = pd.Series(obj.to_numpy())
    return obj