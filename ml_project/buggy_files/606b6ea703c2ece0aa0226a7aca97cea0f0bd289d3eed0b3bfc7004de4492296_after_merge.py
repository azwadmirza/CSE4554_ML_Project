def get_ticker_history(pair: str, tick_interval: str, since_ms: Optional[int] = None) -> List[Dict]:
    try:
        # last item should be in the time interval [now - tick_interval, now]
        till_time_ms = arrow.utcnow().shift(
                        minutes=-constants.TICKER_INTERVAL_MINUTES[tick_interval]
                       ).timestamp * 1000
        # it looks as if some exchanges return cached data
        # and they update it one in several minute, so 10 mins interval
        # is necessary to skeep downloading of an empty array when all
        # chached data was already downloaded
        till_time_ms = min(till_time_ms, arrow.utcnow().shift(minutes=-10).timestamp * 1000)

        data = []
        while not since_ms or since_ms < till_time_ms:
            data_part = _API.fetch_ohlcv(pair, timeframe=tick_interval, since=since_ms)

            if not data_part:
                break

            logger.info('Downloaded data for time range [%s, %s]',
                        arrow.get(data_part[0][0] / 1000).format(),
                        arrow.get(data_part[-1][0] / 1000).format())

            data.extend(data_part)
            since_ms = data[-1][0] + 1

        return data
    except ccxt.NotSupported as e:
        raise OperationalException(
            'Exchange {} does not support fetching historical candlestick data.'
            'Message: {}'.format(_API.name, e)
        )
    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        raise TemporaryError(
            'Could not load ticker history due to {}. Message: {}'.format(
                e.__class__.__name__, e))
    except ccxt.BaseError as e:
        raise OperationalException('Could not fetch ticker data. Msg: {}'.format(e))