    def exchange_currency(self, amount, source_currency, dest_currency):
        if (
            source_currency == dest_currency
            or source_currency == self.default
            or dest_currency == self.default
        ):
            return amount

        rates = self.get_rates()
        source_rate = rates[source_currency]
        dest_rate = rates[dest_currency]
        new_amount = (float(amount) / source_rate) * dest_rate
        # round to two digits because we are dealing with money
        return round(new_amount, 2)