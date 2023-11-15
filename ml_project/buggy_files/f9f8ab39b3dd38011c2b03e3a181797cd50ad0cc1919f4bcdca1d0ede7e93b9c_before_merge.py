    def orderbook(self, pair: str, maximum: int) -> Dict[str, List]:
        """
        fetch latest orderbook data
        :param pair: pair to get the data for
        :param maximum: Maximum number of orderbook entries to query
        :return: dict including bids/asks with a total of `maximum` entries.
        """
        return self._exchange.get_order_book(pair, maximum)