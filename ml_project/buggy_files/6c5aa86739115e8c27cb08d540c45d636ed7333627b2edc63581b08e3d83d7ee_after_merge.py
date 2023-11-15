    def get_currencies(self, with_no_currency=True):
        rates = [
            rate
            for rate in self.get_rates()
            if with_no_currency or rate != self.no_currency
        ]
        rates.sort(key=lambda rate: "" if rate == self.no_currency else rate)
        return rates