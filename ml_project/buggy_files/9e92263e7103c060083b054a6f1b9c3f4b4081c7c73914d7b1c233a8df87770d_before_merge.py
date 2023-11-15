    def _rpc_performance(self) -> List[Dict]:
        """
        Handler for performance.
        Shows a performance statistic from finished trades
        """

        pair_rates = Trade.session.query(Trade.pair,
                                         sql.func.sum(Trade.close_profit).label('profit_sum'),
                                         sql.func.count(Trade.pair).label('count')) \
            .filter(Trade.is_open.is_(False)) \
            .group_by(Trade.pair) \
            .order_by(sql.text('profit_sum DESC')) \
            .all()
        return [
            {'pair': pair, 'profit': round(rate * 100, 2), 'count': count}
            for pair, rate, count in pair_rates
        ]