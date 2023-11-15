def download_pairs(datadir, pairs: List[str],
                   ticker_interval: str,
                   timerange: Optional[Tuple[Tuple, int, int]] = None) -> bool:
    """For each pairs passed in parameters, download the ticker intervals"""
    for pair in pairs:
        try:
            download_backtesting_testdata(datadir,
                                          pair=pair,
                                          tick_interval=ticker_interval,
                                          timerange=timerange)
        except BaseException:
            logger.info(
                'Failed to download the pair: "%s", Interval: %s',
                pair,
                ticker_interval
            )
            return False
    return True