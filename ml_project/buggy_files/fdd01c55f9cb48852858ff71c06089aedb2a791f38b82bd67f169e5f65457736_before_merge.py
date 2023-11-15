    def calculate_fee_rate(self, order: Dict) -> Optional[float]:
        """
        Calculate fee rate if it's not given by the exchange.
        :param order: Order or trade (one trade) dict
        """
        if order['fee'].get('rate') is not None:
            return order['fee'].get('rate')
        fee_curr = order['fee']['currency']
        # Calculate fee based on order details
        if fee_curr in self.get_pair_base_currency(order['symbol']):
            # Base currency - divide by amount
            return round(
                order['fee']['cost'] / safe_value_fallback(order, order, 'filled', 'amount'), 8)
        elif fee_curr in self.get_pair_quote_currency(order['symbol']):
            # Quote currency - divide by cost
            return round(order['fee']['cost'] / order['cost'], 8)
        else:
            # If Fee currency is a different currency
            try:
                comb = self.get_valid_pair_combination(fee_curr, self._config['stake_currency'])
                tick = self.fetch_ticker(comb)

                fee_to_quote_rate = safe_value_fallback(tick, tick, 'last', 'ask')
                return round((order['fee']['cost'] * fee_to_quote_rate) / order['cost'], 8)
            except DependencyException:
                return None