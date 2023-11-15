    def get_buy_rate(self, pair: str, refresh: bool) -> float:
        """
        Calculates bid target between current ask price and last price
        :param pair: Pair to get rate for
        :param refresh: allow cached data
        :return: float: Price
        """
        if not refresh:
            rate = self._buy_rate_cache.get(pair)
            # Check if cache has been invalidated
            if rate:
                logger.info(f"Using cached buy rate for {pair}.")
                return rate

        bid_strategy = self.config.get('bid_strategy', {})
        if 'use_order_book' in bid_strategy and bid_strategy.get('use_order_book', False):
            logger.info(
                f"Getting price from order book {bid_strategy['price_side'].capitalize()} side."
            )
            order_book_top = bid_strategy.get('order_book_top', 1)
            order_book = self.exchange.fetch_l2_order_book(pair, order_book_top)
            logger.debug('order_book %s', order_book)
            # top 1 = index 0
            try:
                rate_from_l2 = order_book[f"{bid_strategy['price_side']}s"][order_book_top - 1][0]
            except (IndexError, KeyError) as e:
                logger.warning(
                    "Buy Price from orderbook could not be determined."
                    f"Orderbook: {order_book}"
                 )
                raise PricingError from e
            logger.info(f'...top {order_book_top} order book buy rate {rate_from_l2:.8f}')
            used_rate = rate_from_l2
        else:
            logger.info(f"Using Last {bid_strategy['price_side'].capitalize()} / Last Price")
            ticker = self.exchange.fetch_ticker(pair)
            ticker_rate = ticker[bid_strategy['price_side']]
            if ticker['last'] and ticker_rate > ticker['last']:
                balance = self.config['bid_strategy']['ask_last_balance']
                ticker_rate = ticker_rate + balance * (ticker['last'] - ticker_rate)
            used_rate = ticker_rate

        self._buy_rate_cache[pair] = used_rate

        return used_rate