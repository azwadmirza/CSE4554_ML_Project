def init_plotscript(config):
    """
    Initialize objects needed for plotting
    :return: Dict with tickers, trades and pairs
    """

    if "pairs" in config:
        pairs = config["pairs"]
    else:
        pairs = config["exchange"]["pair_whitelist"]

    # Set timerange to use
    timerange = TimeRange.parse_timerange(config.get("timerange"))

    tickers = load_data(
        datadir=config.get("datadir"),
        pairs=pairs,
        timeframe=config.get('ticker_interval', '5m'),
        timerange=timerange,
        data_format=config.get('dataformat_ohlcv', 'json'),
    )

    trades = load_trades(config['trade_source'],
                         db_url=config.get('db_url'),
                         exportfilename=config.get('exportfilename'),
                         )
    trades = trim_dataframe(trades, timerange, 'open_time')
    return {"tickers": tickers,
            "trades": trades,
            "pairs": pairs,
            }