    def check_handle_timedout(self) -> None:
        """
        Check if any orders are timed out and cancel if neccessary
        :param timeoutvalue: Number of minutes until order is considered timed out
        :return: None
        """

        for trade in Trade.get_open_order_trades():
            try:
                if not trade.open_order_id:
                    continue
                order = self.exchange.get_order(trade.open_order_id, trade.pair)
            except (RequestException, DependencyException, InvalidOrderException):
                logger.info(
                    'Cannot query order for %s due to %s',
                    trade,
                    traceback.format_exc())
                continue

            # Check if trade is still actually open
            if float(order['remaining']) == 0.0:
                self.wallets.update()
                continue

            if ((order['side'] == 'buy' and order['status'] == 'canceled')
                    or (self._check_timed_out('buy', order))):

                self.handle_timedout_limit_buy(trade, order)
                self.wallets.update()

            elif ((order['side'] == 'sell' and order['status'] == 'canceled')
                  or (self._check_timed_out('sell', order))):
                self.handle_timedout_limit_sell(trade, order)
                self.wallets.update()