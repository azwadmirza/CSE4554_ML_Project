    def initialize(self, **kwargs):
        # TODO: Change to initialize actual parameter (e.g. lengthscale) rather than untransformed parameter.
        """
        Set a value for a parameter

        kwargs: (param_name, value) - parameter to initialize
        Value can take the form of a tensor, a float, or an int
        """
        from .utils.log_deprecation import MODULES_WITH_LOG_PARAMS

        for name, val in kwargs.items():
            if isinstance(val, int):
                val = float(val)
            if any(isinstance(self, mod_type) for mod_type in MODULES_WITH_LOG_PARAMS) and "log_" in name:
                base_name = name.split("log_")[1]
                name = "raw_" + base_name
                if not torch.is_tensor(val):
                    val = self._inv_param_transform(torch.tensor(val).exp()).item()
                else:
                    val = self._inv_param_transform(val.exp())

            if not hasattr(self, name):
                raise AttributeError("Unknown parameter {p} for {c}".format(p=name, c=self.__class__.__name__))
            elif name not in self._parameters:
                setattr(self, name, val)
            elif torch.is_tensor(val):
                try:
                    self.__getattr__(name).data.copy_(val.expand_as(self.__getattr__(name)))
                except RuntimeError:
                    self.__getattr__(name).data.copy_(val.view_as(self.__getattr__(name)))

            elif isinstance(val, float):
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