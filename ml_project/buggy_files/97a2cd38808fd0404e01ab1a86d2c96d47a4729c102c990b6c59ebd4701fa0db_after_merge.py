    def get_trade_stake_amount(self, pair: str) -> float:
        """
        Calculate stake amount for the trade
        :return: float: Stake amount
        :raise: DependencyException if the available stake amount is too low
        """
        stake_amount: float
        # Ensure wallets are uptodate.
        self.wallets.update()

        if self.edge:
            stake_amount = self.edge.stake_amount(
                pair,
                self.wallets.get_free(self.config['stake_currency']),
                self.wallets.get_total(self.config['stake_currency']),
                Trade.total_open_trades_stakes()
            )
        else:
            stake_amount = self.config['stake_amount']
            if stake_amount == constants.UNLIMITED_STAKE_AMOUNT:
                stake_amount = self._calculate_unlimited_stake_amount()

        return self._check_available_stake_amount(stake_amount)