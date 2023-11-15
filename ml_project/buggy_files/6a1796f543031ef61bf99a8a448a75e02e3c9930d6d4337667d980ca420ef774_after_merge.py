def create_trade(stake_amount: float) -> Optional[Trade]:
    """
    Checks the implemented trading indicator(s) for a randomly picked pair,
    if one pair triggers the buy_signal a new trade record gets created
    :param stake_amount: amount of btc to spend
    """
    logger.info(
        'Checking buy signals to create a new trade with stake_amount: %f ...',
        stake_amount
    )
    whitelist = copy.deepcopy(_CONF['exchange']['pair_whitelist'])
    # Check if stake_amount is fulfilled
    if exchange.get_balance(_CONF['stake_currency']) < stake_amount:
        raise FreqtradeException(
            'stake amount is not fulfilled (currency={})'.format(_CONF['stake_currency'])
        )

    # Remove currently opened and latest pairs from whitelist
    for trade in Trade.query.filter(Trade.is_open.is_(True)).all():
        if trade.pair in whitelist:
            whitelist.remove(trade.pair)
            logger.debug('Ignoring %s in pair whitelist', trade.pair)
    if not whitelist:
        raise FreqtradeException('No pair in whitelist')

    # Pick pair based on StochRSI buy signals
    for _pair in whitelist:
        if get_buy_signal(_pair):
            pair = _pair
            break
    else:
        return None

    # Calculate amount and subtract fee
    fee = exchange.get_fee()
    buy_limit = get_target_bid(exchange.get_ticker(pair))
    amount = (1 - fee) * stake_amount / buy_limit

    order_id = exchange.buy(pair, buy_limit, amount)
    # Create trade entity and return
    message = '*{}:* Buying [{}]({}) with limit `{:.8f}`'.format(
        exchange.get_name().upper(),
        pair.replace('_', '/'),
        exchange.get_pair_detail_url(pair),
        buy_limit
    )
    logger.info(message)
    telegram.send_msg(message)
    # Fee is applied twice because we make a LIMIT_BUY and LIMIT_SELL
    return Trade(pair=pair,
                 stake_amount=stake_amount,
                 amount=amount,
                 fee=fee * 2,
                 open_rate=buy_limit,
                 open_date=datetime.utcnow(),
                 exchange=exchange.get_name().upper(),
                 open_order_id=order_id)