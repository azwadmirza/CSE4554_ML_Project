    def _rpc_performance(self) -> List[Dict[str, Any]]:
        """
        Handler for performance.
        Shows a performance statistic from finished trades
        """
        pair_rates = Trade.get_overall_performance()
        # Round and convert to %
        [x.update({'profit': round(x['profit'] * 100, 2)}) for x in pair_rates]
        return pair_rates