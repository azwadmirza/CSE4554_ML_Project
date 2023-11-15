    def validate_timeframes(self, timeframe: List[str]) -> None:
        """
        Checks if ticker interval from config is a supported timeframe on the exchange
        """
        if not hasattr(self._api, "timeframes"):
            # If timeframes is missing, the exchange probably has no fetchOHLCV method.
            # Therefore we also show that.
            raise OperationalException(
                f"This exchange ({self.name}) does not have a `timeframes` attribute and "
                f"is therefore not supported. fetchOHLCV: {self.exchange_has('fetchOHLCV')}")
        timeframes = self._api.timeframes
        if timeframe not in timeframes:
            raise OperationalException(
                f'Invalid ticker {timeframe}, this Exchange supports {timeframes}')