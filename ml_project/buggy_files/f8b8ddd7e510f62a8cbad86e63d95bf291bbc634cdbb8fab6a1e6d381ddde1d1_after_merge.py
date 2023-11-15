    def buy(self, pair: str, ordertype: str, amount: float,
            rate: float, time_in_force: str) -> Dict:

        if self._config['dry_run']:
            dry_order = self.dry_run_order(pair, ordertype, "buy", amount, rate)
            return dry_order

        params = self._params.copy()
        if time_in_force != 'gtc' and ordertype != 'market':
            params.update({'timeInForce': time_in_force})

        return self.create_order(pair, ordertype, 'buy', amount, rate, params)