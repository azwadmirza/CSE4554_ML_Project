def _process(dynamic_whitelist: Optional[bool] = False) -> bool:
    """
    Queries the persistence layer for open trades and handles them,
    otherwise a new trade is created.
    :param: dynamic_whitelist: True is a dynamic whitelist should be generated (optional)
    :return: True if a trade has been created or closed, False otherwise
    """
    state_changed = False
    try:
        # Refresh whitelist based on wallet maintenance
        refresh_whitelist(
            gen_pair_whitelist(_CONF['stake_currency']) if dynamic_whitelist else None
        )
        # Query trades from persistence layer
        trades = Trade.query.filter(Trade.is_open.is_(True)).all()
        if len(trades) < _CONF['max_open_trades']:
            try:
                # Create entity and execute trade
                trade = create_trade(float(_CONF['stake_amount']))
                if trade:
                    Trade.session.add(trade)
                    state_changed = True
                else:
                    logger.info(
                        'Checked all whitelisted currencies. '
                        'Found no suitable entry positions for buying. Will keep looking ...'
                    )
            except FreqtradeException as e:
                logger.warning('Unable to create trade: %s', e)

        for trade in trades:
            # Get order details for actual price per unit
            if trade.open_order_id:
                # Update trade with order values
                logger.info('Got open order for %s', trade)
                trade.update(exchange.get_order(trade.open_order_id))

            if not close_trade_if_fulfilled(trade):
                # Check if we can sell our current pair
                state_changed = handle_trade(trade) or state_changed

            Trade.session.flush()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as error:
        logger.warning(
            'Got %s in _process(), retrying in 30 seconds...',
            error
        )
        time.sleep(30)
    except RuntimeError:
        telegram.send_msg('*Status:* Got RuntimeError:\n```\n{traceback}```{hint}'.format(
            traceback=traceback.format_exc(),
            hint='Issue `/start` if you think it is safe to restart.'
        ))
        logger.exception('Got RuntimeError. Stopping trader ...')
        update_state(State.STOPPED)
    return state_changed