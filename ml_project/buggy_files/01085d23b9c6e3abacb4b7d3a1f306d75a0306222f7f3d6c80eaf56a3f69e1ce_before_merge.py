    def validate_required_startup_candles(self, startup_candles) -> None:
        """
        Checks if required startup_candles is more than ohlcv_candle_limit.
        Requires a grace-period of 5 candles - so a startup-period up to 494 is allowed by default.
        """
        if startup_candles + 5 > self._ft_has['ohlcv_candle_limit']:
            raise OperationalException(
                f"This strategy requires {startup_candles} candles to start. "
                f"{self.name} only provides {self._ft_has['ohlcv_candle_limit']}.")