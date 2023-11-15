    def calculate(self) -> bool:
        pairs = self.config['exchange']['pair_whitelist']
        heartbeat = self.edge_config.get('process_throttle_secs')

        if (self._last_updated > 0) and (
                self._last_updated + heartbeat > arrow.utcnow().timestamp):
            return False

        data: Dict[str, Any] = {}
        logger.info('Using stake_currency: %s ...', self.config['stake_currency'])
        logger.info('Using local backtesting data (using whitelist in given config) ...')

        if self._refresh_pairs:
            history.refresh_data(
                datadir=self.config['datadir'],
                pairs=pairs,
                exchange=self.exchange,
                timeframe=self.strategy.ticker_interval,
                timerange=self._timerange,
            )

        data = history.load_data(
            datadir=self.config['datadir'],
            pairs=pairs,
            timeframe=self.strategy.ticker_interval,
            timerange=self._timerange,
            startup_candles=self.strategy.startup_candle_count,
            data_format=self.config.get('dataformat_ohlcv', 'json'),
        )

        if not data:
            # Reinitializing cached pairs
            self._cached_pairs = {}
            logger.critical("No data found. Edge is stopped ...")
            return False

        preprocessed = self.strategy.tickerdata_to_dataframe(data)

        # Print timeframe
        min_date, max_date = history.get_timerange(preprocessed)
        logger.info(
            'Measuring data from %s up to %s (%s days) ...',
            min_date.isoformat(),
            max_date.isoformat(),
            (max_date - min_date).days
        )
        headers = ['date', 'buy', 'open', 'close', 'sell', 'high', 'low']

        trades: list = []
        for pair, pair_data in preprocessed.items():
            # Sorting dataframe by date and reset index
            pair_data = pair_data.sort_values(by=['date'])
            pair_data = pair_data.reset_index(drop=True)

            ticker_data = self.strategy.advise_sell(
                self.strategy.advise_buy(pair_data, {'pair': pair}), {'pair': pair})[headers].copy()

            trades += self._find_trades_for_stoploss_range(ticker_data, pair, self._stoploss_range)

        # If no trade found then exit
        if len(trades) == 0:
            logger.info("No trades found.")
            return False

        # Fill missing, calculable columns, profit, duration , abs etc.
        trades_df = self._fill_calculable_fields(DataFrame(trades))
        self._cached_pairs = self._process_expectancy(trades_df)
        self._last_updated = arrow.utcnow().timestamp

        return True