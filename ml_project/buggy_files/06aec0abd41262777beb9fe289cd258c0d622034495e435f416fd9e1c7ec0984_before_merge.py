def generate_text_table_strategy(stake_currency: str, max_open_trades: str,
                                 all_results: Dict) -> str:
    """
    Generate summary table per strategy
    :param stake_currency: stake-currency - used to correctly name headers
    :param max_open_trades: Maximum allowed open trades used for backtest
    :param all_results: Dict of <Strategyname: BacktestResult> containing results for all strategies
    :return: pretty printed table with tabulate as string
    """

    floatfmt = ('s', 'd', '.2f', '.2f', '.8f', '.2f', 'd', '.1f', '.1f')
    tabular_data = []
    headers = ['Strategy', 'buy count', 'avg profit %', 'cum profit %',
               f'tot profit {stake_currency}', 'tot profit %', 'avg duration',
               'profit', 'loss']
    for strategy, results in all_results.items():
        tabular_data.append([
            strategy,
            len(results.index),
            results.profit_percent.mean() * 100.0,
            results.profit_percent.sum() * 100.0,
            results.profit_abs.sum(),
            results.profit_percent.sum() * 100.0 / max_open_trades,
            str(timedelta(
                minutes=round(results.trade_duration.mean()))) if not results.empty else '0:00',
            len(results[results.profit_abs > 0]),
            len(results[results.profit_abs < 0])
        ])
    # Ignore type as floatfmt does allow tuples but mypy does not know that
    return tabulate(tabular_data, headers=headers,
                    floatfmt=floatfmt, tablefmt="pipe")  # type: ignore