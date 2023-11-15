def _try_timestamp(x):
    try:
        return pd.Timestamp(x)
    except (ValueError, TypeError):
        return x