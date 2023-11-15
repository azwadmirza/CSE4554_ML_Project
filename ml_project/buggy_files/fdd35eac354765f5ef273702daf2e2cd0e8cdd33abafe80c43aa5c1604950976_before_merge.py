def parse_ticker_dataframe(ticker: list, timeframe: str, pair: str, *,
                           fill_missing: bool = True,
                           drop_incomplete: bool = True) -> DataFrame:
    """
    Converts a ticker-list (format ccxt.fetch_ohlcv) to a Dataframe
    :param ticker: ticker list, as returned by exchange.async_get_candle_history
    :param timeframe: timeframe (e.g. 5m). Used to fill up eventual missing data
    :param pair: Pair this data is for (used to warn if fillup was necessary)
    :param fill_missing: fill up missing candles with 0 candles
                         (see ohlcv_fill_up_missing_data for details)
    :param drop_incomplete: Drop the last candle of the dataframe, assuming it's incomplete
    :return: DataFrame
    """
    logger.debug("Parsing tickerlist to dataframe")
    cols = ['date', 'open', 'high', 'low', 'close', 'volume']
    frame = DataFrame(ticker, columns=cols)

    frame['date'] = to_datetime(frame['date'],
                                unit='ms',
                                utc=True,
                                infer_datetime_format=True)

    # Some exchanges return int values for volume and even for ohlc.
    # Convert them since TA-LIB indicators used in the strategy assume floats
    # and fail with exception...
    frame = frame.astype(dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float',
                                'volume': 'float'})

    # group by index and aggregate results to eliminate duplicate ticks
    frame = frame.groupby(by='date', as_index=False, sort=True).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'max',
    })
    # eliminate partial candle
    if drop_incomplete:
        frame.drop(frame.tail(1).index, inplace=True)
        logger.debug('Dropping last candle')

    if fill_missing:
        return ohlcv_fill_up_missing_data(frame, timeframe, pair)
    else:
        return frame