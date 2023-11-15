    def _top_k(self,
               configs: typing.List[Configuration],
               run_history: RunHistory,
               k: int) -> typing.List[Configuration]:
        """
        Selects the top 'k' configurations from the given list based on their performance.

        This retrieves the performance for each configuration from the runhistory and checks
        that the highest budget they've been evaluated on is the same for each of the configurations.

        Parameters
        ----------
        configs: typing.List[Configuration]
            list of configurations to filter from
        run_history: smac.runhistory.runhistory.RunHistory
            stores all runs we ran so far
        k: int
            number of configurations to select

        Returns
        -------
        typing.List[Configuration]
            top challenger configurations, sorted in increasing costs
        """
        # extracting costs for each given configuration
        config_costs = {}
        # sample list instance-seed-budget key to act as base
        run_key = run_history.get_runs_for_config(configs[0], only_max_observed_budget=True)
        for c in configs:
            # ensuring that all configurations being compared are run on the same set of instance, seed & budget
            cur_run_key = run_history.get_runs_for_config(c, only_max_observed_budget=True)
            if cur_run_key != run_key:
                raise ValueError(
                    'Cannot compare configs that were run on different instances-seeds-budgets: %s vs %s'
                    % (run_key, cur_run_key)
                )
            config_costs[c] = run_history.get_cost(c)

        configs_sorted = sorted(config_costs, key=config_costs.get)
        # select top configurations only
        top_configs = configs_sorted[:k]
        return top_configs