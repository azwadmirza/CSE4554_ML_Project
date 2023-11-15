    def _rpc_forcebuy(self, pair: str, price: Optional[float]) -> Optional[Trade]:
        """
        Handler for forcebuy <asset> <price>
        Buys a pair trade at the given or current price
        """

        if not self._freqtrade.config.get('forcebuy_enable', False):
            raise RPCException('Forcebuy not enabled.')

        if self._freqtrade.state != State.RUNNING:
            raise RPCException('trader is not running')

        # Check pair is in stake currency
        stake_currency = self._freqtrade.config.get('stake_currency')
        if not pair.endswith(stake_currency):
            raise RPCException(
                f'Wrong pair selected. Please pairs with stake {stake_currency} pairs only')
        # check if valid pair

        # check if pair already has an open pair
        trade = Trade.query.filter(Trade.is_open.is_(True)).filter(Trade.pair.is_(pair)).first()
        if trade:
            raise RPCException(f'position for {pair} already open - id: {trade.id}')

        # gen stake amount
        stakeamount = self._freqtrade._get_trade_stake_amount(pair)

        # execute buy
        if self._freqtrade.execute_buy(pair, stakeamount, price):
            trade = Trade.query.filter(Trade.is_open.is_(True)).filter(Trade.pair.is_(pair)).first()
            return trade
        else:
            return None