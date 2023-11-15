    async def async_get_candles_history(self, pairs: List[str],
                                        tick_interval: str) -> List[Tuple[str, List]]:
        """Download ohlcv history for pair-list asyncronously """
        # Calculating ticker interval in second
        interval_in_sec = constants.TICKER_INTERVAL_MINUTES[tick_interval] * 60
        input_coroutines = []

        # Gather corotines to run
        for pair in pairs:
            if not (self._pairs_last_refresh_time.get(pair, 0) + interval_in_sec >=
                    arrow.utcnow().timestamp and pair in self._klines):
                input_coroutines.append(self._async_get_candle_history(pair, tick_interval))
            else:
                logger.debug("Using cached klines data for %s ...", pair)

        tickers = await asyncio.gather(*input_coroutines, return_exceptions=True)

        # handle caching
        for pair, ticks in tickers:
            # keeping last candle time as last refreshed time of the pair
            if ticks:
                self._pairs_last_refresh_time[pair] = ticks[-1][0] // 1000
            # keeping parsed dataframe in cache
            self._klines[pair] = parse_ticker_dataframe(ticks, tick_interval, fill_missing=True)
        return tickers