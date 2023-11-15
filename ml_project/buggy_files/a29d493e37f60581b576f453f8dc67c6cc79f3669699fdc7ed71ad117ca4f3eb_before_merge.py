def _try_unix_timestamp(x):
    try:
        return pd.Timestamp.fromtimestamp(int(x))
    except (ValueError, TypeError):
        return x