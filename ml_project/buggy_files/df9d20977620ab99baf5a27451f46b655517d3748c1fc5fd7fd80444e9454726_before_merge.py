    def get_buy_rate(self, pair: str, tick: Dict = None) -> float:
        """
        Calculates bid target between current ask price and last price
        :return: float: Price
        """
        config_bid_strategy = self.config.get('bid_strategy', {})
        if 'use_order_book' in config_bid_strategy and\
                config_bid_strategy.get('use_order_book', False):
            logger.info('Getting price from order book')
            order_book_top = config_bid_strategy.get('order_book_top', 1)
            order_book = self.exchange.get_order_book(pair, order_book_top)
            logger.debug('order_book %s', order_book)
            # top 1 = index 0
            order_book_rate = order_book['bids'][order_book_top - 1][0]
            logger.info('...top %s order book buy rate %0.8f', order_book_top, order_book_rate)
            used_rate = order_book_rate
        else:
            if not tick:
                logger.info('Using Last Ask / Last Price')
                ticker = self.exchange.fetch_ticker(pair)
            else:
                ticker = tick
            if ticker['ask'] < ticker['last']:
                ticker_rate = ticker['ask']
            else:
                balance = self.config['bid_strategy']['ask_last_balance']
                ticker_rate = ticker['ask'] + balance * (ticker['last'] - ticker['ask'])
            used_rate = ticker_rate

        return used_rate