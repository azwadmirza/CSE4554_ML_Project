    def filter_pairlist(self, pairlist: List[str], tickers: Dict) -> List[str]:
        """
        Filters and sorts pairlists and assigns and returns them again.
        """
        stoploss = self._config.get('stoploss')
        if stoploss is not None:
            # Precalculate sanitized stoploss value to avoid recalculation for every pair
            stoploss = 1 - abs(stoploss)
        # Copy list since we're modifying this list
        for p in deepcopy(pairlist):
            ticker = tickers.get(p)
            # Filter out assets which would not allow setting a stoploss
            if not ticker or (stoploss and not self._validate_precision_filter(ticker, stoploss)):
                pairlist.remove(p)
                continue

        return pairlist