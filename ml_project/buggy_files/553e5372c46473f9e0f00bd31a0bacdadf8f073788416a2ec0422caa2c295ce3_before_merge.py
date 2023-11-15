    def get_sell_rate(self, pair: str, refresh: bool) -> float:
        """
        Get sell rate - either using ticker bid or first bid based on orderbook
        The orderbook portion is only used for rpc messaging, which would otherwise fail
        for BitMex (has no bid/ask in fetch_ticker)
        or remain static in any other case since it's not updating.
        :param pair: Pair to get rate for
        :param refresh: allow cached data
        :return: Bid rate
        """
        if not refresh:
            rate = self._sell_rate_cache.get(pair)
            # Check if cache has been invalidated
            if rate:
                logger.info(f"Using cached sell rate for {pair}.")
                return rate

        ask_strategy = self.config.get('ask_strategy', {})
        if ask_strategy.get('use_order_book', False):
            # This code is only used for notifications, selling uses the generator directly
            logger.info(
                f"Getting price from order book {ask_strategy['price_side'].capitalize()} side."
            )
            rate = next(self._order_book_gen(pair, f"{ask_strategy['price_side']}s"))

        else:
            rate = self.exchange.fetch_ticker(pair)[ask_strategy['price_side']]
        self._sell_rate_cache[pair] = rate
        return rate