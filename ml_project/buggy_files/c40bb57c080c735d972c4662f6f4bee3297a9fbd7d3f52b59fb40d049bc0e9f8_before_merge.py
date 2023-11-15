    async def _async_get_candle_history(self, pair: str, tick_interval: str,
                                        since_ms: Optional[int] = None) -> Tuple[str, List]:
        try:
            # fetch ohlcv asynchronously
            logger.debug("fetching %s since %s ...", pair, since_ms)

            data = await self._api_async.fetch_ohlcv(pair, timeframe=tick_interval,
                                                     since=since_ms)

            # Because some exchange sort Tickers ASC and other DESC.
            # Ex: Bittrex returns a list of tickers ASC (oldest first, newest last)
            # when GDAX returns a list of tickers DESC (newest first, oldest last)
            # Only sort if necessary to save computing time
            if data and data[0][0] > data[-1][0]:
                data = sorted(data, key=lambda x: x[0])

            logger.debug("done fetching %s ...", pair)
            return pair, data

        except ccxt.NotSupported as e:
            raise OperationalException(
                f'Exchange {self._api.name} does not support fetching historical candlestick data.'
                f'Message: {e}')
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not load ticker history due to {e.__class__.__name__}. Message: {e}')
        except ccxt.BaseError as e:
            raise OperationalException(f'Could not fetch ticker data. Msg: {e}')