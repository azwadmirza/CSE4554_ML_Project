    def handle_trailing_stoploss_on_exchange(self, trade: Trade, order):
        """
        Check to see if stoploss on exchange should be updated
        in case of trailing stoploss on exchange
        :param Trade: Corresponding Trade
        :param order: Current on exchange stoploss order
        :return: None
        """

        if trade.stop_loss > float(order['info']['stopPrice']):
            # we check if the update is neccesary
            update_beat = self.strategy.order_types.get('stoploss_on_exchange_interval', 60)
            if (datetime.utcnow() - trade.stoploss_last_update).total_seconds() > update_beat:
                # cancelling the current stoploss on exchange first
                logger.info('Trailing stoploss: cancelling current stoploss on exchange (id:{%s})'
                            'in order to add another one ...', order['id'])
                if self.exchange.cancel_order(order['id'], trade.pair):
                    # creating the new one
                    stoploss_order_id = self.exchange.stoploss_limit(
                        pair=trade.pair, amount=trade.amount,
                        stop_price=trade.stop_loss, rate=trade.stop_loss * 0.99
                    )['id']
                    trade.stoploss_order_id = str(stoploss_order_id)