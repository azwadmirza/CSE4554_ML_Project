    def get_sell_rate(self, pair: str, refresh: bool) -> float:
        """
        Get sell rate - either using get-ticker bid or first bid based on orderbook
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

        config_ask_strategy = self.config.get('ask_strategy', {})
        if config_ask_strategy.get('use_order_book', False):
            logger.debug('Using order book to get sell rate')

            order_book = self.exchange.get_order_book(pair, 1)
            rate = order_book['bids'][0][0]

        else:
            rate = self.exchange.fetch_ticker(pair)['bid']
        self._sell_rate_cache[pair] = rate
        return rate