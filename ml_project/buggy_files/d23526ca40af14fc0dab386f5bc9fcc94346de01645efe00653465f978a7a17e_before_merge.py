    def process(self) -> None:
        """
        Queries the persistence layer for open trades and handles them,
        otherwise a new trade is created.
        :return: True if one or more trades has been created or closed, False otherwise
        """

        # Check whether markets have to be reloaded
        self.exchange._reload_markets()

        # Query trades from persistence layer
        trades = Trade.get_open_trades()

        self.active_pair_whitelist = self._refresh_whitelist(trades)

        # Refreshing candles
        self.dataprovider.refresh(self._create_pair_whitelist(self.active_pair_whitelist),
                                  self.strategy.informative_pairs())

        # Protect from collisions with forcesell.
        # Without this, freqtrade my try to recreate stoploss_on_exchange orders
        # while selling is in process, since telegram messages arrive in an different thread.
        with self._sell_lock:
            # First process current opened trades (positions)
            self.exit_positions(trades)

        # Then looking for buy opportunities
        if self.get_free_open_trades():
            self.enter_positions()

        # Check and handle any timed out open orders
        self.check_handle_timedout()
        Trade.session.flush()

        if (self.heartbeat_interval
                and (arrow.utcnow().timestamp - self._heartbeat_msg > self.heartbeat_interval)):
            logger.info(f"Bot heartbeat. PID={getpid()}")
            self._heartbeat_msg = arrow.utcnow().timestamp