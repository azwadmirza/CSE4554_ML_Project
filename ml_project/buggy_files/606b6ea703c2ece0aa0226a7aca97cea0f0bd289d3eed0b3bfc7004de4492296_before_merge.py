def get_ticker_history(pair: str, tick_interval: str) -> List[Dict]:
    try:
        return _API.fetch_ohlcv(pair, timeframe=tick_interval)
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