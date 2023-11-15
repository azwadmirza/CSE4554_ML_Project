    def adjust_stop_loss(self, current_price: float, stoploss: float, initial: bool = False):
        """
        This adjusts the stop loss to it's most recently observed setting
        :param current_price: Current rate the asset is traded
        :param stoploss: Stoploss as factor (sample -0.05 -> -5% below current price).
        :param initial: Called to initiate stop_loss.
            Skips everything if self.stop_loss is already set.
        """
        if initial and not (self.stop_loss is None or self.stop_loss == 0):
            # Don't modify if called with initial and nothing to do
            return

        new_loss = float(current_price * (1 - abs(stoploss)))

        # no stop loss assigned yet
        if not self.stop_loss:
            logger.debug(f"{self.pair} - Assigning new stoploss...")
            self.stop_loss = new_loss
            self.stop_loss_pct = -1 * abs(stoploss)
            self.initial_stop_loss = new_loss
            self.initial_stop_loss_pct = -1 * abs(stoploss)
            self.stoploss_last_update = datetime.utcnow()

        # evaluate if the stop loss needs to be updated
        else:
            if new_loss > self.stop_loss:  # stop losses only walk up, never down!
                logger.debug(f"{self.pair} - Adjusting stoploss...")
                self.stop_loss = new_loss
                self.stop_loss_pct = -1 * abs(stoploss)
                self.stoploss_last_update = datetime.utcnow()
            else:
                logger.debug(f"{self.pair} - Keeping current stoploss...")

        logger.debug(
            f"{self.pair} - Stoploss adjusted. current_price={current_price:.8f}, "
            f"open_rate={self.open_rate:.8f}, max_rate={self.max_rate:.8f}, "
            f"initial_stop_loss={self.initial_stop_loss:.8f}, "
            f"stop_loss={self.stop_loss:.8f}. "
            f"Trailing stoploss saved us: "
            f"{float(self.stop_loss) - float(self.initial_stop_loss):.8f}.")