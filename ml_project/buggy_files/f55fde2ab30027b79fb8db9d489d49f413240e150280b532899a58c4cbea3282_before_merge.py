def _balance(bot: Bot, update: Update) -> None:
    """
    Handler for /balance
    Returns current account balance per crypto
    """
    output = ""
    balances = exchange.get_balances()
    for currency in balances:
        if not currency['Balance'] and not currency['Available'] and not currency['Pending']:
            continue
        output += """*Currency*: {Currency}
*Available*: {Available}
*Balance*: {Balance}
*Pending*: {Pending}

""".format(**currency)

    send_msg(output)