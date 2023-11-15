def load_trades_from_db(db_url: str) -> pd.DataFrame:
    """
    Load trades from a DB (using dburl)
    :param db_url: Sqlite url (default format sqlite:///tradesv3.dry-run.sqlite)
    :return: Dataframe containing Trades
    """
    trades: pd.DataFrame = pd.DataFrame([], columns=BT_DATA_COLUMNS)
    persistence.init(db_url, clean_open_orders=False)
    columns = ["pair", "profit", "open_time", "close_time",
               "open_rate", "close_rate", "duration", "sell_reason",
               "max_rate", "min_rate"]

    trades = pd.DataFrame([(t.pair, t.calc_profit(),
                            t.open_date.replace(tzinfo=pytz.UTC),
                            t.close_date.replace(tzinfo=pytz.UTC) if t.close_date else None,
                            t.open_rate, t.close_rate,
                            t.close_date.timestamp() - t.open_date.timestamp()
                            if t.close_date else None,
                            t.sell_reason,
                            t.max_rate,
                            t.min_rate,
                            )
                           for t in Trade.query.all()],
                          columns=columns)

    return trades