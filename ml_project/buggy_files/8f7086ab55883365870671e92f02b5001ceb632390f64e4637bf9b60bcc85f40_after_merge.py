    def fetch_ticker(self, pair: str) -> dict:
        try:
            if pair not in self._api.markets or not self._api.markets[pair].get('active'):
                raise DependencyException(f"Pair {pair} not available")
            data = self._api.fetch_ticker(pair)
            return data
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not load ticker due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e