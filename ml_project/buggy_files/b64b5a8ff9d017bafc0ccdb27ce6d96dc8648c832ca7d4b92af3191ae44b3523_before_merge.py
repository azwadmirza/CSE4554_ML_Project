def load_data(datadir: str,
              ticker_interval: str,
              pairs: Optional[List[str]] = None,
              refresh_pairs: Optional[bool] = False,
              timerange: Optional[Tuple[Tuple, int, int]] = None) -> Dict[str, List]:
    """
    Loads ticker history data for the given parameters
    :return: dict
    """
    result = {}

    _pairs = pairs or hyperopt_optimize_conf()['exchange']['pair_whitelist']

    # If the user force the refresh of pairs
    if refresh_pairs:
        logger.info('Download data for all pairs and store them in %s', datadir)
        download_pairs(datadir, _pairs, ticker_interval)

    for pair in _pairs:
        pairdata = load_tickerdata_file(datadir, pair, ticker_interval, timerange=timerange)
        if not pairdata:
            # download the tickerdata from exchange
            download_backtesting_testdata(datadir, pair=pair, interval=ticker_interval)
            # and retry reading the pair
            pairdata = load_tickerdata_file(datadir, pair, ticker_interval, timerange=timerange)
        result[pair] = pairdata
    return result