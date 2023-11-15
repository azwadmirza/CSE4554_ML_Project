def init_plotscript(config):
    """
    Initialize objects needed for plotting
    :return: Dict with tickers, trades, pairs and strategy
    """
    exchange: Optional[Exchange] = None

    # Exchange is only needed when downloading data!
    if config.get("live", False) or config.get("refresh_pairs", False):
        exchange = ExchangeResolver(config.get('exchange', {}).get('name'),
                                    config).exchange

    strategy = StrategyResolver(config).strategy
    if "pairs" in config:
        pairs = config["pairs"].split(',')
    else:
        pairs = config["exchange"]["pair_whitelist"]

    # Set timerange to use
    timerange = Arguments.parse_timerange(config.get("timerange"))

    tickers = history.load_data(
        datadir=Path(str(config.get("datadir"))),
        pairs=pairs,
        ticker_interval=config['ticker_interval'],
        refresh_pairs=config.get('refresh_pairs', False),
        timerange=timerange,
        exchange=exchange,
        live=config.get("live", False),
    )

    trades = load_trades(config)
    return {"tickers": tickers,
            "trades": trades,
            "pairs": pairs,
            "strategy": strategy,
            }