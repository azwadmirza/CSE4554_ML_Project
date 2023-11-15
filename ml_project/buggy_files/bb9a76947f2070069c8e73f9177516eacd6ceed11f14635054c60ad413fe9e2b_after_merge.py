def check_handle_timedout(timeoutvalue: int) -> None:
    """
    Check if any orders are timed out and cancel if neccessary
    :param timeoutvalue: Number of minutes until order is considered timed out
    :return: None
    """
    timeoutthreashold = arrow.utcnow().shift(minutes=-timeoutvalue).datetime

    for trade in Trade.query.filter(Trade.open_order_id.isnot(None)).all():
        try:
            order = exchange.get_order(trade.open_order_id)
        except requests.exceptions.RequestException:
            logger.info('Cannot query order for %s due to %s', trade, traceback.format_exc())
            continue
        ordertime = arrow.get(order['opened'])

        # Check if trade is still actually open
        if int(order['remaining']) == 0:
            continue

        if order['type'] == "LIMIT_BUY" and ordertime < timeoutthreashold:
            # Buy timeout - cancel order
            exchange.cancel_order(trade.open_order_id)
            if order['remaining'] == order['amount']:
                # if trade is not partially completed, just delete the trade
                Trade.session.delete(trade)
                Trade.session.flush()
                logger.info('Buy order timeout for %s.', trade)
                rpc.send_msg('*Timeout:* Unfilled buy order for {} cancelled'.format(
                             trade.pair.replace('_', '/')))
            else:
                # if trade is partially complete, edit the stake details for the trade
                # and close the order
                trade.amount = order['amount'] - order['remaining']
                trade.stake_amount = trade.amount * trade.open_rate
                trade.open_order_id = None
                logger.info('Partial buy order timeout for %s.', trade)
                rpc.send_msg('*Timeout:* Remaining buy order for {} cancelled'.format(
                             trade.pair.replace('_', '/')))
        elif order['type'] == "LIMIT_SELL" and ordertime < timeoutthreashold:
            # Sell timeout - cancel order and update trade
            if order['remaining'] == order['amount']:
                # if trade is not partially completed, just cancel the trade
                exchange.cancel_order(trade.open_order_id)
                trade.close_rate = None
                trade.close_profit = None
                trade.close_date = None
                trade.is_open = True
                trade.open_order_id = None
                rpc.send_msg('*Timeout:* Unfilled sell order for {} cancelled'.format(
                             trade.pair.replace('_', '/')))
                logger.info('Sell order timeout for %s.', trade)
                return True
            else:
                # TODO: figure out how to handle partially complete sell orders
                pass