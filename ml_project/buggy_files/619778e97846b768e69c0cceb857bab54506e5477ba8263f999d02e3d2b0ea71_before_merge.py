    def _add_distributions(
        self, distributions: Dict[str, optuna.distributions.BaseDistribution]
    ) -> None:
        for param_name, param_distribution in distributions.items():
            if isinstance(param_distribution, optuna.distributions.UniformDistribution):
                self._hp_params[param_name] = hp.HParam(
                    param_name, hp.RealInterval(param_distribution.low, param_distribution.high)
                )
            elif isinstance(param_distribution, optuna.distributions.LogUniformDistribution):
                self._hp_params[param_name] = hp.HParam(
                    param_name, hp.RealInterval(param_distribution.low, param_distribution.high)
                )
            elif isinstance(param_distribution, optuna.distributions.DiscreteUniformDistribution):
                self._hp_params[param_name] = hp.HParam(
                    param_name, hp.RealInterval(param_distribution.low, param_distribution.high)
                )
            elif isinstance(param_distribution, optuna.distributions.IntUniformDistribution):
                self._hp_params[param_name] = hp.HParam(
                    param_name, hp.IntInterval(param_distribution.low, param_distribution.high)
                )
            elif isinstance(param_distribution, optuna.distributions.CategoricalDistribution):
                self._hp_params[param_name] = hp.HParam(
                    param_name, hp.Discrete(param_distribution.choices)
                )
            else:
                distribution_list = [
                    optuna.distributions.UniformDistribution.__name__,
                    optuna.distributions.LogUniformDistribution.__name__,
                    optuna.distributions.DiscreteUniformDistribution.__name__,
                    optuna.distributions.IntUniformDistribution.__name__,
                    optuna.distributions.CategoricalDistribution.__name__,
                ]
                raise NotImplementedError(
                    "The distribution {} is not implemented. "
                    "The parameter distribution should be one of the {}".format(
                        param_distribution, distribution_list
                    )
                )