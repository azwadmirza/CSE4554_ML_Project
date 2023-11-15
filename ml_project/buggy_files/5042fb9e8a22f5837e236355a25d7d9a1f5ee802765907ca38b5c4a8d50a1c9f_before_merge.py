    def _find_price(self, crypto_symbol: str, fiat_symbol: str) -> float:
        """
        Call CoinMarketCap API to retrieve the price in the FIAT
        :param crypto_symbol: Crypto-currency you want to convert (e.g BTC)
        :param fiat_symbol: FIAT currency you want to convert to (e.g USD)
        :return: float, price of the crypto-currency in Fiat
        """
        # Check if the fiat convertion you want is supported
        if not self._is_supported_fiat(fiat=fiat_symbol):
            raise ValueError('The fiat {} is not supported.'.format(fiat_symbol))

        return float(
            self._coinmarketcap.ticker(
                currency=crypto_symbol,
                convert=fiat_symbol
            )['price_' + fiat_symbol.lower()]
        )