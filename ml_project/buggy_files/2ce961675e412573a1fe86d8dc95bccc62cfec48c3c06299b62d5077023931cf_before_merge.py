def load_trades_from_db(db_url: str) -> pd.DataFrame:
    """
    Load trades from a DB (using dburl)
    :param db_url: Sqlite url (default format sqlite:///tradesv3.dry-run.sqlite)
    :return: Dataframe containing Trades
    """
    trades: pd.DataFrame = pd.DataFrame([], columns=BT_DATA_COLUMNS)
    persistence.init(db_url, clean_open_orders=False)

    columns = ["pair", "open_time", "close_time", "profit", "profitperc",
               "open_rate", "close_rate", "amount", "duration", "sell_reason",
               "fee_open", "fee_close", "open_rate_requested", "close_rate_requested",
               "stake_amount", "max_rate", "min_rate", "id", "exchange",
               "stop_loss", "initial_stop_loss", "strategy", "ticker_interval"]

    trades = pd.DataFrame([(t.pair,
                            t.open_date.replace(tzinfo=pytz.UTC),
                            t.close_date.replace(tzinfo=pytz.UTC) if t.close_date else None,
                            t.calc_profit(), t.calc_profit_percent(),
                            t.open_rate, t.close_rate, t.amount,
                            (round((t.close_date.timestamp() - t.open_date.timestamp()) / 60, 2)
                                if t.close_date else None),
                            t.sell_reason,
                            t.fee_open, t.fee_close,
                            t.open_rate_requested,
                            t.close_rate_requested,
                            t.stake_amount,
                            t.max_rate,
                            t.min_rate,
                            t.id, t.exchange,
                            t.stop_loss, t.initial_stop_loss,
                            t.strategy, t.ticker_interval
                            )
                           for t in Trade.query.all()],
                          columns=columns)

    return trades