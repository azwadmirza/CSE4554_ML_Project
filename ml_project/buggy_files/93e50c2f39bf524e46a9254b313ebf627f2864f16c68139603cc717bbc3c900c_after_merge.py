    def handle_stoploss_on_exchange(self, trade: Trade) -> bool:
        """
        Check if trade is fulfilled in which case the stoploss
        on exchange should be added immediately if stoploss on exchange
        is enabled.
        """

        logger.debug('Handling stoploss on exchange %s ...', trade)

        stoploss_order = None

        try:
            # First we check if there is already a stoploss on exchange
            stoploss_order = self.exchange.get_order(trade.stoploss_order_id, trade.pair) \
                if trade.stoploss_order_id else None
        except InvalidOrderException as exception:
            logger.warning('Unable to fetch stoploss order: %s', exception)

        # We check if stoploss order is fulfilled
        if stoploss_order and stoploss_order['status'] == 'closed':
            trade.sell_reason = SellType.STOPLOSS_ON_EXCHANGE.value
            trade.update(stoploss_order)
            # Lock pair for one candle to prevent immediate rebuys
            self.strategy.lock_pair(trade.pair,
                                    timeframe_to_next_date(self.config['ticker_interval']))
            self._notify_sell(trade, "stoploss")
            return True

        if trade.open_order_id or not trade.is_open:
            # Trade has an open Buy or Sell order, Stoploss-handling can't happen in this case
            # as the Amount on the exchange is tied up in another trade.
            # The trade can be closed already (sell-order fill confirmation came in this iteration)
            return False

        # If buy order is fulfilled but there is no stoploss, we add a stoploss on exchange
        if (not stoploss_order):

            stoploss = self.edge.stoploss(pair=trade.pair) if self.edge else self.strategy.stoploss

            stop_price = trade.open_rate * (1 + stoploss)

            if self.create_stoploss_order(trade=trade, stop_price=stop_price, rate=stop_price):
                trade.stoploss_last_update = datetime.now()
                return False

        # If stoploss order is canceled for some reason we add it
        if stoploss_order and stoploss_order['status'] == 'canceled':
            if self.create_stoploss_order(trade=trade, stop_price=trade.stop_loss,
                                          rate=trade.stop_loss):
                return False
            else:
                trade.stoploss_order_id = None
                logger.warning('Stoploss order was cancelled, but unable to recreate one.')

        # Finally we check if stoploss on exchange should be moved up because of trailing.
        if stoploss_order and self.config.get('trailing_stop', False):
            # if trailing stoploss is enabled we check if stoploss value has changed
            # in which case we cancel stoploss order and put another one with new
            # value immediately
            self.handle_trailing_stoploss_on_exchange(trade, stoploss_order)

        return False