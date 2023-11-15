    def amount_to_precision(self, pair, amount: float) -> float:
        '''
        Returns the amount to buy or sell to a precision the Exchange accepts
        Reimplementation of ccxt internal methods - ensuring we can test the result is correct
        based on our definitions.
        '''
        if self.markets[pair]['precision']['amount']:
            amount = float(decimal_to_precision(amount, rounding_mode=TRUNCATE,
                                                precision=self.markets[pair]['precision']['amount'],
                                                counting_mode=self.precisionMode,
                                                ))

        return amount