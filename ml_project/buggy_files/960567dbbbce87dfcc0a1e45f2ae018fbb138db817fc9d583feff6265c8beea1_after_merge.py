    def execute_sell(self, trade: Trade, limit: float, sell_reason: SellType) -> None:
        """
        Executes a limit sell for the given trade and limit
        :param trade: Trade instance
        :param limit: limit rate for the sell order
        :param sellreason: Reason the sell was triggered
        :return: None
        """
        sell_type = 'sell'
        if sell_reason in (SellType.STOP_LOSS, SellType.TRAILING_STOP_LOSS):
            sell_type = 'stoploss'

        # if stoploss is on exchange and we are on dry_run mode,
        # we consider the sell price stop price
        if self.config.get('dry_run', False) and sell_type == 'stoploss' \
           and self.strategy.order_types['stoploss_on_exchange']:
            limit = trade.stop_loss

        # First cancelling stoploss on exchange ...
        if self.strategy.order_types.get('stoploss_on_exchange') and trade.stoploss_order_id:
            try:
                self.exchange.cancel_order(trade.stoploss_order_id, trade.pair)
            except InvalidOrderException:
                logger.exception(f"Could not cancel stoploss order {trade.stoploss_order_id}")

        # Execute sell and update trade record
        order_id = self.exchange.sell(pair=str(trade.pair),
                                      ordertype=self.strategy.order_types[sell_type],
                                      amount=trade.amount, rate=limit,
                                      time_in_force=self.strategy.order_time_in_force['sell']
                                      )['id']

        trade.open_order_id = order_id
        trade.close_rate_requested = limit
        trade.sell_reason = sell_reason.value
        Trade.session.flush()
        self.notify_sell(trade)