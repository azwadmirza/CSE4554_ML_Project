    def create_stoploss_order(self, trade: Trade, stop_price: float, rate: float) -> bool:
        """
        Abstracts creating stoploss orders from the logic.
        Handles errors and updates the trade database object.
        Force-sells the pair (using EmergencySell reason) in case of Problems creating the order.
        :return: True if the order succeeded, and False in case of problems.
        """
        # Limit price threshold: As limit price should always be below stop-price
        LIMIT_PRICE_PCT = self.strategy.order_types.get('stoploss_on_exchange_limit_ratio', 0.99)

        try:
            stoploss_order = self.exchange.stoploss_limit(pair=trade.pair, amount=trade.amount,
                                                          stop_price=stop_price,
                                                          rate=rate * LIMIT_PRICE_PCT)
            trade.stoploss_order_id = str(stoploss_order['id'])
            return True
        except InvalidOrderException as e:
            trade.stoploss_order_id = None
            logger.error(f'Unable to place a stoploss order on exchange. {e}')
            logger.warning('Selling the trade forcefully')
            self.execute_sell(trade, trade.stop_loss, sell_reason=SellType.EMERGENCY_SELL)

        except DependencyException:
            trade.stoploss_order_id = None
            logger.exception('Unable to place a stoploss order on exchange.')
        return False