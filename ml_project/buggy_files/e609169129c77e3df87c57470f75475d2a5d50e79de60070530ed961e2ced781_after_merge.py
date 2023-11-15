    def _process_expectancy(self, results: DataFrame) -> Dict[str, Any]:
        """
        This calculates WinRate, Required Risk Reward, Risk Reward and Expectancy of all pairs
        The calulation will be done per pair and per strategy.
        """
        # Removing pairs having less than min_trades_number
        min_trades_number = self.edge_config.get('min_trade_number', 10)
        results = results.groupby(['pair', 'stoploss']).filter(lambda x: len(x) > min_trades_number)
        ###################################

        # Removing outliers (Only Pumps) from the dataset
        # The method to detect outliers is to calculate standard deviation
        # Then every value more than (standard deviation + 2*average) is out (pump)
        #
        # Removing Pumps
        if self.edge_config.get('remove_pumps', False):
            results = results[results['profit_abs'] < 2 * results['profit_abs'].std()
                              + results['profit_abs'].mean()]
        ##########################################################################

        # Removing trades having a duration more than X minutes (set in config)
        max_trade_duration = self.edge_config.get('max_trade_duration_minute', 1440)
        results = results[results.trade_duration < max_trade_duration]
        #######################################################################

        if results.empty:
            return {}

        groupby_aggregator = {
            'profit_abs': [
                ('nb_trades', 'count'),  # number of all trades
                ('profit_sum', lambda x: x[x > 0].sum()),  # cumulative profit of all winning trades
                ('loss_sum', lambda x: abs(x[x < 0].sum())),  # cumulative loss of all losing trades
                ('nb_win_trades', lambda x: x[x > 0].count())  # number of winning trades
            ],
            'trade_duration': [('avg_trade_duration', 'mean')]
        }

        # Group by (pair and stoploss) by applying above aggregator
        df = results.groupby(['pair', 'stoploss'])[['profit_abs', 'trade_duration']].agg(
            groupby_aggregator).reset_index(col_level=1)

        # Dropping level 0 as we don't need it
        df.columns = df.columns.droplevel(0)

        # Calculating number of losing trades, average win and average loss
        df['nb_loss_trades'] = df['nb_trades'] - df['nb_win_trades']
        df['average_win'] = df['profit_sum'] / df['nb_win_trades']
        df['average_loss'] = df['loss_sum'] / df['nb_loss_trades']

        # Win rate = number of profitable trades / number of trades
        df['winrate'] = df['nb_win_trades'] / df['nb_trades']

        # risk_reward_ratio = average win / average loss
        df['risk_reward_ratio'] = df['average_win'] / df['average_loss']

        # required_risk_reward = (1 / winrate) - 1
        df['required_risk_reward'] = (1 / df['winrate']) - 1

        # expectancy = (risk_reward_ratio * winrate) - (lossrate)
        df['expectancy'] = (df['risk_reward_ratio'] * df['winrate']) - (1 - df['winrate'])

        # sort by expectancy and stoploss
        df = df.sort_values(by=['expectancy', 'stoploss'], ascending=False).groupby(
            'pair').first().sort_values(by=['expectancy'], ascending=False).reset_index()

        final = {}
        for x in df.itertuples():
            final[x.pair] = PairInfo(
                x.stoploss,
                x.winrate,
                x.risk_reward_ratio,
                x.required_risk_reward,
                x.expectancy,
                x.nb_trades,
                x.avg_trade_duration
            )

        # Returning a list of pairs in order of "expectancy"
        return final