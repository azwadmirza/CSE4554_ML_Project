def load_pair_history(pair: str,
                      timeframe: str,
                      datadir: Path,
                      timerange: Optional[TimeRange] = None,
                      refresh_pairs: bool = False,
                      exchange: Optional[Exchange] = None,
                      fill_up_missing: bool = True,
                      drop_incomplete: bool = True,
                      startup_candles: int = 0,
                      ) -> DataFrame:
    """
    Loads cached ticker history for the given pair.
    :param pair: Pair to load data for
    :param timeframe: Ticker timeframe (e.g. "5m")
    :param datadir: Path to the data storage location.
    :param timerange: Limit data to be loaded to this timerange
    :param refresh_pairs: Refresh pairs from exchange.
        (Note: Requires exchange to be passed as well.)
    :param exchange: Exchange object (needed when using "refresh_pairs")
    :param fill_up_missing: Fill missing values with "No action"-candles
    :param drop_incomplete: Drop last candle assuming it may be incomplete.
    :param startup_candles: Additional candles to load at the start of the period
    :return: DataFrame with ohlcv data
    """

    timerange_startup = deepcopy(timerange)
    if startup_candles > 0 and timerange_startup:
        timerange_startup.subtract_start(timeframe_to_seconds(timeframe) * startup_candles)

    # The user forced the refresh of pairs
    if refresh_pairs:
        download_pair_history(datadir=datadir,
                              exchange=exchange,
                              pair=pair,
                              timeframe=timeframe,
                              timerange=timerange)

    pairdata = load_tickerdata_file(datadir, pair, timeframe, timerange=timerange_startup)

    if pairdata:
        if timerange_startup:
            _validate_pairdata(pair, pairdata, timerange_startup)
        return parse_ticker_dataframe(pairdata, timeframe, pair=pair,
                                      fill_missing=fill_up_missing,
                                      drop_incomplete=drop_incomplete)
    else:
        logger.warning(
            f'No history data for pair: "{pair}", timeframe: {timeframe}. '
            'Use `freqtrade download-data` to download the data'
        )
        return None