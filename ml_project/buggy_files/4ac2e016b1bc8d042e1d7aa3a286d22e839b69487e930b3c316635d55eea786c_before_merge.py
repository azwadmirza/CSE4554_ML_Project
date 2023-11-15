    def handle_timedout_limit_sell(self, trade: Trade, order: Dict) -> bool:
        """
        Sell timeout - cancel order and update trade
        :return: True if order was fully cancelled
        """
        if order['remaining'] == order['amount']:
            # if trade is not partially completed, just cancel the trade
            if order["status"] != "canceled":
                reason = "due to timeout"
                self.exchange.cancel_order(trade.open_order_id, trade.pair)
                logger.info('Sell order timeout for %s.', trade)
            else:
                reason = "on exchange"
                logger.info('Sell order canceled on exchange for %s.', trade)
            trade.close_rate = None
            trade.close_profit = None
            trade.close_date = None
            trade.is_open = True
            trade.open_order_id = None
            self.rpc.send_msg({
                'type': RPCMessageType.STATUS_NOTIFICATION,
                'status': f'Unfilled sell order for {trade.pair} cancelled {reason}'
            })

            return True

        # TODO: figure out how to handle partially complete sell orders
        return False