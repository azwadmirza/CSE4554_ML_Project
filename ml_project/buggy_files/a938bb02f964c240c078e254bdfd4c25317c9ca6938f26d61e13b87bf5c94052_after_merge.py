    def _get_min_pair_stake_amount(self, pair: str, price: float) -> Optional[float]:
        markets = self.exchange.get_markets()
        markets = [m for m in markets if m['symbol'] == pair]
        if not markets:
            raise ValueError(f'Can\'t get market information for symbol {pair}')

        market = markets[0]

        if 'limits' not in market:
            return None

        min_stake_amounts = []
        limits = market['limits']
        if ('cost' in limits and 'min' in limits['cost']
                and limits['cost']['min'] is not None):
            min_stake_amounts.append(limits['cost']['min'])

        if ('amount' in limits and 'min' in limits['amount']
                and limits['amount']['min'] is not None):
            min_stake_amounts.append(limits['amount']['min'] * price)

        if not min_stake_amounts:
            return None

        amount_reserve_percent = 1 - 0.05  # reserve 5% + stoploss
        if self.analyze.get_stoploss() is not None:
            amount_reserve_percent += self.analyze.get_stoploss()
        # it should not be more than 50%
        amount_reserve_percent = max(amount_reserve_percent, 0.5)
        return min(min_stake_amounts)/amount_reserve_percent