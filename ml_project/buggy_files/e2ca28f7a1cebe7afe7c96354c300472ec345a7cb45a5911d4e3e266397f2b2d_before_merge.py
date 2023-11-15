    def tickerdata_to_dataframe(self, tickerdata: Dict[str, List]) -> Dict[str, DataFrame]:
        """
        Creates a dataframe and populates indicators for given ticker data
        Used by optimize operations only, not during dry / live runs.
        """
        return {pair: self.advise_indicators(pair_data, {'pair': pair})
                for pair, pair_data in tickerdata.items()}