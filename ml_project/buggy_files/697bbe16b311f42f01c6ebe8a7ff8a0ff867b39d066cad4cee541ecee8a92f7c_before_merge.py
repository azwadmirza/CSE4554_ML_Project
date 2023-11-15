def create_trade(stake_amount: float, interval: int) -> bool:
    """
    Checks the implemented trading indicator(s) for a randomly picked pair,
    if one pair triggers the buy_signal a new trade record gets created
    :param stake_amount: amount of btc to spend
    :return: True if a trade object has been created and persisted, False otherwise
    """
    logger.info(
        'Checking buy signals to create a new trade with stake_amount: %f ...',
        stake_amount
    )
    whitelist = copy.deepcopy(_CONF['exchange']['pair_whitelist'])
    # Check if stake_amount is fulfilled
    if exchange.get_balance(_CONF['stake_currency']) < stake_amount:
        raise DependencyException(
            'stake amount is not fulfilled (currency={})'.format(_CONF['stake_currency'])
        )

    # Remove currently opened and latest pairs from whitelist
    for trade in Trade.query.filter(Trade.is_open.is_(True)).all():
        if trade.pair in whitelist:
            whitelist.remove(trade.pair)
            logger.debug('Ignoring %s in pair whitelist', trade.pair)
    if not whitelist:
        raise DependencyException('No pair in whitelist')

    # Pick pair based on StochRSI buy signals
    for _pair in whitelist:
        (buy, sell) = get_signal(_pair)
        if buy and not sell:
            pair = _pair
            break
    else:
        return False

    # Calculate amount
    buy_limit = get_target_bid(exchange.get_ticker(pair))
    amount = stake_amount / buy_limit

    order_id = exchange.buy(pair, buy_limit, amount)

    fiat_converter = CryptoToFiatConverter()
    stake_amount_fiat = fiat_converter.convert_amount(
        stake_amount,
        _CONF['stake_currency'],
        _CONF['fiat_display_currency']
    )

    # Create trade entity and return
    rpc.send_msg('*{}:* Buying [{}]({}) with limit `{:.8f} ({:.6f} {}, {:.3f} {})` '.format(
        exchange.get_name().upper(),
        pair.replace('_', '/'),
        exchange.get_pair_detail_url(pair),
        buy_limit, stake_amount, _CONF['stake_currency'],
        stake_amount_fiat, _CONF['fiat_display_currency']
    ))
    # Fee is applied twice because we make a LIMIT_BUY and LIMIT_SELL
    trade = Trade(
        pair=pair,
        stake_amount=stake_amount,
        amount=amount,
        fee=exchange.get_fee(),
        open_rate=buy_limit,
        open_date=datetime.utcnow(),
        exchange=exchange.get_name().upper(),
        open_order_id=order_id
    )
    Trade.session.add(trade)
    Trade.session.flush()
    return True