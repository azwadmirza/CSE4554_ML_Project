def build_empty_series(dtype, index=None, name=None):
    length = len(index) if index is not None else 0
    return pd.Series([_generate_value(dtype, 1) for _ in range(length)],
                     dtype=dtype, index=index, name=name)