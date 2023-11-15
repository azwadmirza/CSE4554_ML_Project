def rolling_max(series, window=14, min_periods=None):
    min_periods = window if min_periods is None else min_periods
    try:
        return series.rolling(window=window, min_periods=min_periods).max()
    except Exception as e:  # noqa: F841
        return pd.Series(series).rolling(window=window, min_periods=min_periods).max()