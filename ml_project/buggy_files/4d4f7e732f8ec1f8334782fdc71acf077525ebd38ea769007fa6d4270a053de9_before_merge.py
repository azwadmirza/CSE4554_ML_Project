    def _order_book_gen(self, pair: str, side: str, order_book_max: int = 1,
                        order_book_min: int = 1):
        """
        Helper generator to query orderbook in loop (used for early sell-order placing)
        """
        order_book = self.exchange.get_order_book(pair, order_book_max)
        for i in range(order_book_min, order_book_max + 1):
            yield order_book[side][i - 1][0]