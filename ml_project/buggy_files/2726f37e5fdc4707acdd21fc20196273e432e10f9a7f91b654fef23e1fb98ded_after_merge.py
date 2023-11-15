def _try_timestamp(x):
    try:
        ts = pd.Timestamp(x)
        return ts.to_pydatetime()
    except (ValueError, TypeError):
        return x