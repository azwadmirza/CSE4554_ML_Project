    def _rpc_status_table(self, stake_currency, fiat_display_currency: str) -> Tuple[List, List]:
        trades = Trade.get_open_trades()
        if not trades:
            raise RPCException('no active trade')
        else:
            trades_list = []
            for trade in trades:
                # calculate profit and send message to user
                try:
                    current_rate = self._freqtrade.get_sell_rate(trade.pair, False)
                except DependencyException:
                    current_rate = NAN
                trade_perc = (100 * trade.calc_profit_ratio(current_rate))
                trade_profit = trade.calc_profit(current_rate)
                profit_str = f'{trade_perc:.2f}%'
                if self._fiat_converter:
                    fiat_profit = self._fiat_converter.convert_amount(
                            trade_profit,
                            stake_currency,
                            fiat_display_currency
                        )
                    if fiat_profit and not isnan(fiat_profit):
                        profit_str += f" ({fiat_profit:.2f})"
                trades_list.append([
                    trade.id,
                    trade.pair,
                    shorten_date(arrow.get(trade.open_date).humanize(only_distance=True)),
                    profit_str
                ])
            profitcol = "Profit"
            if self._fiat_converter:
                profitcol += " (" + fiat_display_currency + ")"

            columns = ['ID', 'Pair', 'Since', profitcol]
            return trades_list, columns