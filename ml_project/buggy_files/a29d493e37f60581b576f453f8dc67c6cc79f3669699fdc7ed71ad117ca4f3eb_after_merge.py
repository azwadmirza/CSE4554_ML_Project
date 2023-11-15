def _try_unix_timestamp(x):
    try:
        ts = pd.Timestamp.fromtimestamp(int(x))
        return ts.to_pydatetime()
    except (ValueError, TypeError):
        return x