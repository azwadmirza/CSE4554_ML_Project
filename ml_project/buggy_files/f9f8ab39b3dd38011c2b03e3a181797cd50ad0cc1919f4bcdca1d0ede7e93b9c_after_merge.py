    def orderbook(self, pair: str, maximum: int) -> Dict[str, List]:
        """
        Fetch latest l2 orderbook data
        Warning: Does a network request - so use with common sense.
        :param pair: pair to get the data for
        :param maximum: Maximum number of orderbook entries to query
        :return: dict including bids/asks with a total of `maximum` entries.
        """
        return self._exchange.fetch_l2_order_book(pair, maximum)