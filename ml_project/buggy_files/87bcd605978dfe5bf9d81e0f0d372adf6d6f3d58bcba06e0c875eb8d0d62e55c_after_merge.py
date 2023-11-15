    def initialize(self, **kwargs):
        """
        Set a value for a parameter

        kwargs: (param_name, value) - parameter to initialize.
        Can also initialize recursively by passing in the full name of a
        parameter. For example if model has attribute model.likelihood,
        we can initialize the noise with either
        `model.initialize(**{'likelihood.noise': 0.1})`
        or
        `model.likelihood.initialize(noise=0.1)`.
        The former method would allow users to more easily store the
        initialization values as one object.

        Value can take the form of a tensor, a float, or an int
        """

        for name, val in kwargs.items():
            if isinstance(val, int):
                val = float(val)
            if '.' in name:
                module, name = self._get_module_and_name(name)
                module.initialize(**{name: val})
            elif not hasattr(self, name):
                raise AttributeError("Unknown parameter {p} for {c}".format(p=name, c=self.__class__.__name__))
            elif name not in self._parameters:
                setattr(self, name, val)
            elif torch.is_tensor(val):
                constraint = self.constraint_for_parameter_name(name)
                if constraint is not None and not constraint.check_raw(val):
                    raise RuntimeError(
                        "Attempting to manually set a parameter value that is out of bounds of "
                        f"its current constraints, {constraint}. "
                        "Most likely, you want to do the following:\n likelihood = GaussianLikelihood"
                        "(noise_constraint=gpytorch.constraints.GreaterThan(better_lower_bound))"
                    )
                try:
                    self.__getattr__(name).data.copy_(val.expand_as(self.__getattr__(name)))
                except RuntimeError:
                    self.__getattr__(name).data.copy_(val.view_as(self.__getattr__(name)))

            elif isinstance(val, float):
                constraint = self.constraint_for_parameter_name(name)
                if constraint is not None and not constraint.check_raw(val):
                    raise RuntimeError(
                        "Attempting to manually set a parameter value that is out of bounds of "
                        f"its current constraints, {constraint}. "
                        "Most likely, you want to do the following:\n likelihood = GaussianLikelihood"
                        "(noise_constraint=gpytorch.constraints.GreaterThan(better_lower_bound))"
                    )
                self.__getattr__(name).data.fill_(val)
            else:
                raise AttributeError("Type {t} not valid for initializing parameter {p}".format(t=type(val), p=name))

            # Ensure value is contained in support of prior (if present)
            prior_name = "_".join([name, "prior"])
            if prior_name in self._priors:
                prior, closure, _ = self._priors[prior_name]
                try:
                    prior._validate_sample(closure())
                except ValueError as e:
                    raise ValueError("Invalid input value for prior {}. Error:\n{}".format(prior_name, e))

        return self