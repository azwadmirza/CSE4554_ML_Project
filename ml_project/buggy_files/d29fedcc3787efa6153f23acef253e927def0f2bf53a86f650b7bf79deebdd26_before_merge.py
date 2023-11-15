def load_data(datadir: Path,
              timeframe: str,
              pairs: List[str],
              refresh_pairs: bool = False,
              exchange: Optional[Exchange] = None,
              timerange: Optional[TimeRange] = None,
              fill_up_missing: bool = True,
              startup_candles: int = 0,
              fail_without_data: bool = False
              ) -> Dict[str, DataFrame]:
    """
    Loads ticker history data for a list of pairs
    :param datadir: Path to the data storage location.
    :param timeframe: Ticker Timeframe (e.g. "5m")
    :param pairs: List of pairs to load
    :param refresh_pairs: Refresh pairs from exchange.
        (Note: Requires exchange to be passed as well.)
    :param exchange: Exchange object (needed when using "refresh_pairs")
    :param timerange: Limit data to be loaded to this timerange
    :param fill_up_missing: Fill missing values with "No action"-candles
    :param startup_candles: Additional candles to load at the start of the period
    :param fail_without_data: Raise OperationalException if no data is found.
    :return: dict(<pair>:<Dataframe>)
    TODO: refresh_pairs is still used by edge to keep the data uptodate.
        This should be replaced in the future. Instead, writing the current candles to disk
        from dataprovider should be implemented, as this would avoid loading ohlcv data twice.
        exchange and refresh_pairs are then not needed here nor in load_pair_history.
    """
    result: Dict[str, DataFrame] = {}
    if startup_candles > 0 and timerange:
        logger.info(f'Using indicator startup period: {startup_candles} ...')

    for pair in pairs:
        hist = load_pair_history(pair=pair, timeframe=timeframe,
                                 datadir=datadir, timerange=timerange,
                                 refresh_pairs=refresh_pairs,
                                 exchange=exchange,
                                 fill_up_missing=fill_up_missing,
                                 startup_candles=startup_candles)
        if hist is not None:
            result[pair] = hist

    if fail_without_data and not result:
        raise OperationalException("No data found. Terminating.")
    return result