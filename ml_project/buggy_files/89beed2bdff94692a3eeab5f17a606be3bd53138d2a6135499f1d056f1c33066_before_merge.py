    def check_handle_timedout(self) -> None:
        """
        Check if any orders are timed out and cancel if neccessary
        :param timeoutvalue: Number of minutes until order is considered timed out
        :return: None
        """
        buy_timeout = self.config['unfilledtimeout']['buy']
        sell_timeout = self.config['unfilledtimeout']['sell']
        buy_timeout_threshold = arrow.utcnow().shift(minutes=-buy_timeout).datetime
        sell_timeout_threshold = arrow.utcnow().shift(minutes=-sell_timeout).datetime

        for trade in Trade.query.filter(Trade.open_order_id.isnot(None)).all():
            try:
                # FIXME: Somehow the query above returns results
                # where the open_order_id is in fact None.
                # This is probably because the record got
                # updated via /forcesell in a different thread.
                if not trade.open_order_id:
                    continue
                order = self.exchange.get_order(trade.open_order_id, trade.pair)
            except (RequestException, DependencyException, InvalidOrderException):
                logger.info(
                    'Cannot query order for %s due to %s',
                    trade,
                    traceback.format_exc())
                continue
            ordertime = arrow.get(order['datetime']).datetime

            # Check if trade is still actually open
            if float(order['remaining']) == 0.0:
                self.wallets.update()
                continue

            if ((order['side'] == 'buy' and order['status'] == 'canceled')
                or (order['status'] == 'open'
                    and order['side'] == 'buy' and ordertime < buy_timeout_threshold)):

                self.handle_timedout_limit_buy(trade, order)
                self.wallets.update()

            elif ((order['side'] == 'sell' and order['status'] == 'canceled')
                  or (order['status'] == 'open'
                      and order['side'] == 'sell' and ordertime < sell_timeout_threshold)):
                self.handle_timedout_limit_sell(trade, order)
                self.wallets.update()