    def update(self, order: Dict) -> None:
        """
        Updates this entity with amount and actual open/close rates.
        :param order: order retrieved by exchange.get_order()
        :return: None
        """
        order_type = order['type']
        # Ignore open and cancelled orders
        if order['status'] == 'open' or order['price'] is None:
            return

        logger.info('Updating trade (id=%s) ...', self.id)

        if order_type in ('market', 'limit') and order['side'] == 'buy':
            # Update open rate and actual amount
            self.open_rate = Decimal(order['price'])
            self.amount = Decimal(order['amount'])
            self.recalc_open_trade_price()
            logger.info('%s_BUY has been fulfilled for %s.', order_type.upper(), self)
            self.open_order_id = None
        elif order_type in ('market', 'limit') and order['side'] == 'sell':
            self.close(order['price'])
            logger.info('%s_SELL has been fulfilled for %s.', order_type.upper(), self)
        elif order_type in ('stop_loss_limit', 'stop-loss'):
            self.stoploss_order_id = None
            self.close_rate_requested = self.stop_loss
            logger.info('%s is hit for %s.', order_type.upper(), self)
            self.close(order['average'])
        else:
            raise ValueError(f'Unknown order type: {order_type}')
        cleanup()