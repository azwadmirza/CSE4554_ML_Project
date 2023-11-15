    def _load_cryptomap(self) -> None:
        try:
            coinlistings = self._coinmarketcap.listings()
            self._cryptomap = dict(map(lambda coin: (coin["symbol"], str(coin["id"])),
                                       coinlistings["data"]))
        except (ValueError, RequestException) as exception:
            logger.error(
                "Could not load FIAT Cryptocurrency map for the following problem: %s",
                exception
            )