    def _rpc_daily_profit(
            self, timescale: int,
            stake_currency: str, fiat_display_currency: str) -> List[List[Any]]:
        today = datetime.utcnow().date()
        profit_days: Dict[date, Dict] = {}

        if not (isinstance(timescale, int) and timescale > 0):
            raise RPCException('timescale must be an integer greater than 0')

        for day in range(0, timescale):
            profitday = today - timedelta(days=day)
            trades = Trade.get_trades(trade_filter=[
                Trade.is_open.is_(False),
                Trade.close_date >= profitday,
                Trade.close_date < (profitday + timedelta(days=1))
            ]).order_by(Trade.close_date).all()
            curdayprofit = sum(trade.calc_profit() for trade in trades)
            profit_days[profitday] = {
                'amount': f'{curdayprofit:.8f}',
                'trades': len(trades)
            }

        return [
            [
                key,
                '{value:.8f} {symbol}'.format(
                    value=float(value['amount']),
                    symbol=stake_currency
                ),
                '{value:.3f} {symbol}'.format(
                    value=self._fiat_converter.convert_amount(
                        value['amount'],
                        stake_currency,
                        fiat_display_currency
                    ) if self._fiat_converter else 0,
                    symbol=fiat_display_currency
                ),
                '{value} trade{s}'.format(
                    value=value['trades'],
                    s='' if value['trades'] < 2 else 's'
                ),
            ]
            for key, value in profit_days.items()
        ]