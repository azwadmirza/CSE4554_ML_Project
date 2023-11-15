    def handle_trade(self, trade: Trade) -> bool:
        """
        Sells the current pair if the threshold is reached and updates the trade record.
        :return: True if trade has been sold, False otherwise
        """
        if not trade.is_open:
            raise DependencyException(f'Attempt to handle closed trade: {trade}')

        logger.debug('Handling %s ...', trade)

        (buy, sell) = (False, False)

        config_ask_strategy = self.config.get('ask_strategy', {})

        if (config_ask_strategy.get('use_sell_signal', True) or
                config_ask_strategy.get('ignore_roi_if_buy_signal', False)):
            (buy, sell) = self.strategy.get_signal(
                trade.pair, self.strategy.ticker_interval,
                self.dataprovider.ohlcv(trade.pair, self.strategy.ticker_interval))

        if config_ask_strategy.get('use_order_book', False):
            # logger.debug('Order book %s',orderBook)
            order_book_min = config_ask_strategy.get('order_book_min', 1)
            order_book_max = config_ask_strategy.get('order_book_max', 1)
            logger.info(f'Using order book between {order_book_min} and {order_book_max} '
                        f'for selling {trade.pair}...')

            order_book = self._order_book_gen(trade.pair, f"{config_ask_strategy['price_side']}s",
                                              order_book_min=order_book_min,
                                              order_book_max=order_book_max)
            for i in range(order_book_min, order_book_max + 1):
                try:
                    sell_rate = next(order_book)
                except (IndexError, KeyError) as e:
                    logger.warning(
                        f"Sell Price at location {i} from orderbook could not be determined."
                    )
                    raise PricingError from e
                logger.debug(f"  order book {config_ask_strategy['price_side']} top {i}: "
                             f"{sell_rate:0.8f}")

                if self._check_and_execute_sell(trade, sell_rate, buy, sell):
                    return True

        else:
            logger.debug('checking sell')
            sell_rate = self.get_sell_rate(trade.pair, True)
            if self._check_and_execute_sell(trade, sell_rate, buy, sell):
                return True

        logger.debug('Found no sell signal for %s.', trade)
        return False