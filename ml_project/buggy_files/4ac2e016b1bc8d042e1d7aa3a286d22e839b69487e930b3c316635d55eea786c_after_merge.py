    def handle_timedout_limit_sell(self, trade: Trade, order: Dict) -> bool:
        """
        Sell timeout - cancel order and update trade
        :return: True if order was fully cancelled
        """
        # if trade is not partially completed, just cancel the trade
        if order['remaining'] == order['amount']:
            if order["status"] != "canceled":
                reason = "cancelled due to timeout"
                # if trade is not partially completed, just delete the trade
                self.exchange.cancel_order(trade.open_order_id, trade.pair)
                logger.info('Sell order %s for %s.', reason, trade)
            else:
                reason = "cancelled on exchange"
                logger.info('Sell order %s for %s.', reason, trade)

            trade.close_rate = None
            trade.close_profit = None
            trade.close_date = None
            trade.is_open = True
            trade.open_order_id = None

            return True

        # TODO: figure out how to handle partially complete sell orders
        return False