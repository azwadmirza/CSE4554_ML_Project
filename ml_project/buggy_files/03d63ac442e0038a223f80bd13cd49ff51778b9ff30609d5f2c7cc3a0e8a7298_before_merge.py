def handle_trade(trade: Trade, interval: int) -> bool:
    """
    Sells the current pair if the threshold is reached and updates the trade record.
    :return: True if trade has been sold, False otherwise
    """
    if not trade.is_open:
        raise ValueError('attempt to handle closed trade: {}'.format(trade))

    logger.debug('Handling %s ...', trade)
    current_rate = exchange.get_ticker(trade.pair)['bid']

    (buy, sell) = (False, False)

    if _CONF.get('experimental', {}).get('use_sell_signal'):
        (buy, sell) = get_signal(trade.pair)

    # Check if minimal roi has been reached and no longer in buy conditions (avoiding a fee)
    if not buy and min_roi_reached(trade, current_rate, datetime.utcnow()):
        logger.debug('Executing sell due to ROI ...')
        execute_sell(trade, current_rate)
        return True

    # Experimental: Check if the trade is profitable before selling it (avoid selling at loss)
    if _CONF.get('experimental', {}).get('sell_profit_only', False):
        logger.debug('Checking if trade is profitable ...')
        if not buy and trade.calc_profit(rate=current_rate) <= 0:
            return False

    if sell and not buy:
        logger.debug('Executing sell due to sell signal ...')
        execute_sell(trade, current_rate)
        return True

    return False