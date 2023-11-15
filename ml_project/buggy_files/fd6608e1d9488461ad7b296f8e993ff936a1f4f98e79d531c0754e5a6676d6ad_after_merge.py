    def _check_and_execute_sell(self, trade: Trade, sell_rate: float,
                                buy: bool, sell: bool) -> bool:
        """
        Check and execute sell
        """
        should_sell = self.strategy.should_sell(
            trade, sell_rate, datetime.utcnow(), buy, sell,
            force_stoploss=self.edge.stoploss(trade.pair) if self.edge else 0
        )

        if should_sell.sell_flag:
            logger.info(f'Executing Sell for {trade.pair}. Reason: {should_sell.sell_type}')
            self.execute_sell(trade, sell_rate, should_sell.sell_type)
            return True
        return False