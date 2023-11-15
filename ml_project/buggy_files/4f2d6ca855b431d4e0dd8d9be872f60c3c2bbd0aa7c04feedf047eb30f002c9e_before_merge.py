    def _rpc_trade_statistics(
            self, stake_currency: str, fiat_display_currency: str) -> Dict[str, Any]:
        """ Returns cumulative profit statistics """
        trades = Trade.query.order_by(Trade.id).all()

        profit_all_coin = []
        profit_all_perc = []
        profit_closed_coin = []
        profit_closed_perc = []
        durations = []

        for trade in trades:
            current_rate: float = 0.0

            if not trade.open_rate:
                continue
            if trade.close_date:
                durations.append((trade.close_date - trade.open_date).total_seconds())

            if not trade.is_open:
                profit_percent = trade.calc_profit_percent()
                profit_closed_coin.append(trade.calc_profit())
                profit_closed_perc.append(profit_percent)
            else:
                # Get current rate
                try:
                    current_rate = self._freqtrade.get_sell_rate(trade.pair, False)
                except DependencyException:
                    current_rate = NAN
                profit_percent = trade.calc_profit_percent(rate=current_rate)

            profit_all_coin.append(
                trade.calc_profit(rate=Decimal(trade.close_rate or current_rate))
            )
            profit_all_perc.append(profit_percent)

        best_pair = Trade.session.query(
            Trade.pair, sql.func.sum(Trade.close_profit).label('profit_sum')
        ).filter(Trade.is_open.is_(False)) \
            .group_by(Trade.pair) \
            .order_by(sql.text('profit_sum DESC')).first()

        if not best_pair:
            raise RPCException('no closed trade')

        bp_pair, bp_rate = best_pair

        # Prepare data to display
        profit_closed_coin_sum = round(sum(profit_closed_coin), 8)
        profit_closed_percent = (round(mean(profit_closed_perc) * 100, 2) if profit_closed_perc
                                 else 0.0)
        profit_closed_fiat = self._fiat_converter.convert_amount(
            profit_closed_coin_sum,
            stake_currency,
            fiat_display_currency
        ) if self._fiat_converter else 0

        profit_all_coin_sum = round(sum(profit_all_coin), 8)
        profit_all_percent = round(mean(profit_all_perc) * 100, 2) if profit_all_perc else 0.0
        profit_all_fiat = self._fiat_converter.convert_amount(
            profit_all_coin_sum,
            stake_currency,
            fiat_display_currency
        ) if self._fiat_converter else 0

        num = float(len(durations) or 1)
        return {
            'profit_closed_coin': profit_closed_coin_sum,
            'profit_closed_percent': profit_closed_percent,
            'profit_closed_fiat': profit_closed_fiat,
            'profit_all_coin': profit_all_coin_sum,
            'profit_all_percent': profit_all_percent,
            'profit_all_fiat': profit_all_fiat,
            'trade_count': len(trades),
            'first_trade_date': arrow.get(trades[0].open_date).humanize(),
            'latest_trade_date': arrow.get(trades[-1].open_date).humanize(),
            'avg_duration': str(timedelta(seconds=sum(durations) / num)).split('.')[0],
            'best_pair': bp_pair,
            'best_rate': round(bp_rate * 100, 2),
        }