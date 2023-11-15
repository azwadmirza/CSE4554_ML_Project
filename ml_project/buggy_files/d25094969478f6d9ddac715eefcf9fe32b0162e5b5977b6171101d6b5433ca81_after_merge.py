def check_migrate(engine) -> None:
    """
    Checks if migration is necessary and migrates if necessary
    """
    inspector = inspect(engine)

    cols = inspector.get_columns('trades')
    tabs = inspector.get_table_names()
    table_back_name = 'trades_bak'
    for i, table_back_name in enumerate(tabs):
        table_back_name = f'trades_bak{i}'
        logger.debug(f'trying {table_back_name}')

    # Check for latest column
    if not has_column(cols, 'stoploss_order_id'):
        logger.info(f'Running database migration - backup available as {table_back_name}')

        fee_open = get_column_def(cols, 'fee_open', 'fee')
        fee_close = get_column_def(cols, 'fee_close', 'fee')
        open_rate_requested = get_column_def(cols, 'open_rate_requested', 'null')
        close_rate_requested = get_column_def(cols, 'close_rate_requested', 'null')
        stop_loss = get_column_def(cols, 'stop_loss', '0.0')
        initial_stop_loss = get_column_def(cols, 'initial_stop_loss', '0.0')
        stoploss_order_id = get_column_def(cols, 'stoploss_order_id', 'null')
        max_rate = get_column_def(cols, 'max_rate', '0.0')
        sell_reason = get_column_def(cols, 'sell_reason', 'null')
        strategy = get_column_def(cols, 'strategy', 'null')
        ticker_interval = get_column_def(cols, 'ticker_interval', 'null')

        # Schema migration necessary
        engine.execute(f"alter table trades rename to {table_back_name}")
        # drop indexes on backup table
        for index in inspector.get_indexes(table_back_name):
            engine.execute(f"drop index {index['name']}")
        # let SQLAlchemy create the schema as required
        _DECL_BASE.metadata.create_all(engine)

        # Copy data back - following the correct schema
        engine.execute(f"""insert into trades
                (id, exchange, pair, is_open, fee_open, fee_close, open_rate,
                open_rate_requested, close_rate, close_rate_requested, close_profit,
                stake_amount, amount, open_date, close_date, open_order_id,
                stop_loss, initial_stop_loss, stoploss_order_id, max_rate, sell_reason, strategy,
                ticker_interval
                )
            select id, lower(exchange),
                case
                    when instr(pair, '_') != 0 then
                    substr(pair,    instr(pair, '_') + 1) || '/' ||
                    substr(pair, 1, instr(pair, '_') - 1)
                    else pair
                    end
                pair,
                is_open, {fee_open} fee_open, {fee_close} fee_close,
                open_rate, {open_rate_requested} open_rate_requested, close_rate,
                {close_rate_requested} close_rate_requested, close_profit,
                stake_amount, amount, open_date, close_date, open_order_id,
                {stop_loss} stop_loss, {initial_stop_loss} initial_stop_loss,
                {stoploss_order_id} stoploss_order_id, {max_rate} max_rate,
                {sell_reason} sell_reason, {strategy} strategy,
                {ticker_interval} ticker_interval
                from {table_back_name}
             """)

        # Reread columns - the above recreated the table!
        inspector = inspect(engine)
        cols = inspector.get_columns('trades')