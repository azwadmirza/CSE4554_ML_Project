def generate_text_table_sell_reason(data: Dict[str, Dict], results: DataFrame) -> str:
    """
    Generate small table outlining Backtest results
    :param data: Dict of <pair: dataframe> containing data that was used during backtesting.
    :param results: Dataframe containing the backtest results
    :return: pretty printed table with tabulate as string
    """
    tabular_data = []
    headers = ['Sell Reason', 'Count', 'Profit', 'Loss', 'Profit %']
    for reason, count in results['sell_reason'].value_counts().iteritems():
        result = results.loc[results['sell_reason'] == reason]
        profit = len(result[result['profit_abs'] >= 0])
        loss = len(result[result['profit_abs'] < 0])
        profit_mean = round(result['profit_percent'].mean() * 100.0, 2)
        tabular_data.append([reason.value, count, profit, loss, profit_mean])
    return tabulate(tabular_data, headers=headers, tablefmt="pipe")