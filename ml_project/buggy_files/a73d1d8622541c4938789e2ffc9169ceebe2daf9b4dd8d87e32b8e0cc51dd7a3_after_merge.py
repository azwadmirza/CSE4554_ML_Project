def _balance(bot: Bot, update: Update) -> None:
    """
    Handler for /balance
    Returns current account balance per crypto
    """
    output = ''
    balances = [
        c for c in exchange.get_balances()
        if c['Balance'] or c['Available'] or c['Pending']
    ]
    if not balances:
        send_msg('`All balances are zero.`')
        return

    total = 0.0
    for currency in balances:
        coin = currency['Currency']
        if coin == 'BTC':
            currency["Rate"] = 1.0
        else:
            if coin == 'USDT':
                currency["Rate"] = 1.0 / exchange.get_ticker('USDT_BTC', False)['bid']
            else:
                currency["Rate"] = exchange.get_ticker('BTC_' + coin, False)['bid']
        currency['BTC'] = currency["Rate"] * currency["Balance"]
        total = total + currency['BTC']
        output += """*Currency*: {Currency}
*Available*: {Available}
*Balance*: {Balance}
*Pending*: {Pending}
*Est. BTC*: {BTC: .8f}

""".format(**currency)

    symbol = _CONF['fiat_display_currency']
    value = _FIAT_CONVERT.convert_amount(
        total, 'BTC', symbol
    )
    output += """*Estimated Value*:
*BTC*: {0: .8f}
*{1}*: {2: .2f}
""".format(total, symbol, value)
    send_msg(output)