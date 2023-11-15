def trades_to_ohlcv(trades: list, timeframe: str) -> list:
    """
    Converts trades list to ohlcv list
    :param trades: List of trades, as returned by ccxt.fetch_trades.
    :param timeframe: Ticker timeframe to resample data to
    :return: ohlcv timeframe as list (as returned by ccxt.fetch_ohlcv)
    """
    from freqtrade.exchange import timeframe_to_minutes
    ticker_minutes = timeframe_to_minutes(timeframe)
    df = pd.DataFrame(trades)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')

    df_new = df['price'].resample(f'{ticker_minutes}min').ohlc()
    df_new['volume'] = df['amount'].resample(f'{ticker_minutes}min').sum()
    df_new['date'] = df_new.index.astype("int64") // 10 ** 6
    # Drop 0 volume rows
    df_new = df_new.dropna()
    columns = ["date", "open", "high", "low", "close", "volume"]
    return list(zip(*[df_new[x].values.tolist() for x in columns]))