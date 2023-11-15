def generate_text_table_sell_reason(
    data: Dict[str, Dict], stake_currency: str, max_open_trades: int, results: DataFrame
) -> str:
    """
    Generate small table outlining Backtest results
    :param data: Dict of <pair: dataframe> containing data that was used during backtesting.
    :param results: Dataframe containing the backtest results
    :return: pretty printed table with tabulate as string
    """
    tabular_data = []
    headers = [
        "Sell Reason",
        "Sells",
        "Wins",
        "Draws",
        "Losses",
        "Avg Profit %",
        "Cum Profit %",
        f"Tot Profit {stake_currency}",
        "Tot Profit %",
    ]
    for reason, count in results['sell_reason'].value_counts().iteritems():
        result = results.loc[results['sell_reason'] == reason]
        wins = len(result[result['profit_abs'] > 0])
        draws = len(result[result['profit_abs'] == 0])
        loss = len(result[result['profit_abs'] < 0])
        profit_mean = round(result['profit_percent'].mean() * 100.0, 2)
        profit_sum = round(result["profit_percent"].sum() * 100.0, 2)
        profit_tot = result['profit_abs'].sum()
        profit_percent_tot = round(result['profit_percent'].sum() * 100.0 / max_open_trades, 2)
        tabular_data.append(
            [
                reason.value,
                count,
                wins,
                draws,
                loss,
                profit_mean,
                profit_sum,
                profit_tot,
                profit_percent_tot,
            ]
        )
    return tabulate(tabular_data, headers=headers, tablefmt="pipe")