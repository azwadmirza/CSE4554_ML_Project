    def _add_distributions(
        self, distributions: Dict[str, optuna.distributions.BaseDistribution]
    ) -> None:
        real_distributions = (
            optuna.distributions.UniformDistribution,
            optuna.distributions.LogUniformDistribution,
            optuna.distributions.DiscreteUniformDistribution,
        )
        int_distributions = (optuna.distributions.IntUniformDistribution,)
        categorical_distributions = (optuna.distributions.CategoricalDistribution,)
        supported_distributions = (
            real_distributions + int_distributions + categorical_distributions
        )

        for param_name, param_distribution in distributions.items():
            if isinstance(param_distribution, real_distributions):
                self._hp_params[param_name] = hp.HParam(
                    param_name,
                    hp.RealInterval(float(param_distribution.low), float(param_distribution.high)),
                )
            elif isinstance(param_distribution, int_distributions):
                self._hp_params[param_name] = hp.HParam(
                    param_name,
                    hp.IntInterval(param_distribution.low, param_distribution.high),
                )
            elif isinstance(param_distribution, categorical_distributions):
                self._hp_params[param_name] = hp.HParam(
                    param_name,
                    hp.Discrete(param_distribution.choices),
                )
            else:
                distribution_list = [
                    distribution.__name__ for distribution in supported_distributions
                ]
                raise NotImplementedError(
                    "The distribution {} is not implemented. "
                    "The parameter distribution should be one of the {}".format(
                        param_distribution, distribution_list
                    )
                )