    def _validate_ticker_lowprice(self, ticker) -> bool:
        """
        Check if if one price-step (pip) is > than a certain barrier.
        :param ticker: ticker dict as returned from ccxt.load_markets()
        :return: True if the pair can stay, false if it should be removed
        """
        compare = ticker['last'] + self._exchange.price_get_one_pip(ticker['symbol'],
                                                                    ticker['last'])
        changeperc = (compare - ticker['last']) / ticker['last']
        if changeperc > self._low_price_ratio:
            self.log_on_refresh(logger.info, f"Removed {ticker['symbol']} from whitelist, "
                                             f"because 1 unit is {changeperc * 100:.3f}%")
            return False
        return True