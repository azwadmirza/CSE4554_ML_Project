    def _check_depth_of_market_buy(self, pair: str, conf: Dict) -> bool:
        """
        Checks depth of market before executing a buy
        """
        conf_bids_to_ask_delta = conf.get('bids_to_ask_delta', 0)
        logger.info('checking depth of market for %s', pair)
        order_book = self.exchange.get_order_book(pair, 1000)
        order_book_data_frame = order_book_to_dataframe(order_book['bids'], order_book['asks'])
        order_book_bids = order_book_data_frame['b_size'].sum()
        order_book_asks = order_book_data_frame['a_size'].sum()
        bids_ask_delta = order_book_bids / order_book_asks
        logger.info('bids: %s, asks: %s, delta: %s', order_book_bids,
                    order_book_asks, bids_ask_delta)
        if bids_ask_delta >= conf_bids_to_ask_delta:
            return True
        return False