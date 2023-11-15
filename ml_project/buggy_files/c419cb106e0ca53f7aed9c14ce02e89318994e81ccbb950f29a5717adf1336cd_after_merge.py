def trades_to_ohlcv(trades: list, timeframe: str) -> DataFrame:
    """
    Converts trades list to ohlcv list
    TODO: This should get a dedicated test
    :param trades: List of trades, as returned by ccxt.fetch_trades.
    :param timeframe: Ticker timeframe to resample data to
    :return: ohlcv Dataframe.
    """
    from freqtrade.exchange import timeframe_to_minutes
    ticker_minutes = timeframe_to_minutes(timeframe)
    df = pd.DataFrame(trades)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')

    df_new = df['price'].resample(f'{ticker_minutes}min').ohlc()
    df_new['volume'] = df['amount'].resample(f'{ticker_minutes}min').sum()
    df_new['date'] = df_new.index
    # Drop 0 volume rows
    df_new = df_new.dropna()
    return df_new[DEFAULT_DATAFRAME_COLUMNS]