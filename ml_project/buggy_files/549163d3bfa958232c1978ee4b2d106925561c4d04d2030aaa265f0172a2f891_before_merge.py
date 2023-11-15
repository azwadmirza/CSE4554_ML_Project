    def price_to_precision(self, pair, price: float) -> float:
        '''
        Returns the price rounded up to the precision the Exchange accepts.
        Partial Reimplementation of ccxt internal method decimal_to_precision(),
        which does not support rounding up
        TODO: If ccxt supports ROUND_UP for decimal_to_precision(), we could remove this and
        align with amount_to_precision().
        Rounds up
        '''
        if self.markets[pair]['precision']['price']:
            # price = float(decimal_to_precision(price, rounding_mode=ROUND,
            #                                    precision=self.markets[pair]['precision']['price'],
            #                                    counting_mode=self.precisionMode,
            #                                    ))
            if self.precisionMode == TICK_SIZE:
                precision = self.markets[pair]['precision']['price']
                missing = price % precision
                if missing != 0:
                    price = price - missing + precision
            else:
                symbol_prec = self.markets[pair]['precision']['price']
                big_price = price * pow(10, symbol_prec)
                price = ceil(big_price) / pow(10, symbol_prec)
        return price