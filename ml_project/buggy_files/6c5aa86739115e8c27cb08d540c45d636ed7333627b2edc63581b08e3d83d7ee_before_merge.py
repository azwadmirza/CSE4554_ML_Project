    def get_currencies(self):
        rates = [rate for rate in self.get_rates()]
        rates.sort(key=lambda rate: "" if rate == self.default else rate)
        return rates