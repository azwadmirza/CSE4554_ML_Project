def _chunkwise_moments(df):
    df2 = cudf.DataFrame()
    for col in df.columns:
        df2[col] = df[col].astype("float64").pow(2)
    vals = {
        "df-count": df.count().to_frame().transpose(),
        "df-sum": df.sum().to_frame().transpose(),
        "df2-sum": df2.sum().to_frame().transpose(),
    }
    # NOTE: Perhaps we should convert to pandas here
    # (since we know the results should be small)?
    del df2
    return vals