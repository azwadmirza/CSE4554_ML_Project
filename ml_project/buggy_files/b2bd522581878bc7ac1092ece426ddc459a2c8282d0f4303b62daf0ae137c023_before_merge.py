    def create_trade(self, pair: str) -> bool:
        """
        Check the implemented trading strategy for buy signals.

        If the pair triggers the buy signal a new trade record gets created
        and the buy-order opening the trade gets issued towards the exchange.

        :return: True if a trade has been created.
        """
        logger.debug(f"create_trade for pair {pair}")

        if self.strategy.is_pair_locked(pair):
            logger.info(f"Pair {pair} is currently locked.")
            return False

        # running get_signal on historical data fetched
        (buy, sell) = self.strategy.get_signal(
            pair, self.strategy.ticker_interval,
            self.dataprovider.ohlcv(pair, self.strategy.ticker_interval))

        if buy and not sell:
            if not self.get_free_open_trades():
                logger.debug("Can't open a new trade: max number of trades is reached.")
                return False

            stake_amount = self.get_trade_stake_amount(pair)
            if not stake_amount:
                logger.debug("Stake amount is 0, ignoring possible trade for {pair}.")
                return False

            logger.info(f"Buy signal found: about create a new trade with stake_amount: "
                        f"{stake_amount} ...")

            bid_check_dom = self.config.get('bid_strategy', {}).get('check_depth_of_market', {})
            if ((bid_check_dom.get('enabled', False)) and
                    (bid_check_dom.get('bids_to_ask_delta', 0) > 0)):
                if self._check_depth_of_market_buy(pair, bid_check_dom):
                    return self.execute_buy(pair, stake_amount)
                else:
                    return False

            return self.execute_buy(pair, stake_amount)
        else:
            return False