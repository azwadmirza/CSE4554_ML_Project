    def _build(self):
        unconstrained = self._build_parameter()
        constrained = self._build_constrained(unconstrained)
        prior = self._build_prior(unconstrained, constrained)
        self._unconstrained_tensor = unconstrained  # pylint: disable=W0201
        self._constrained_tensor = constrained      # pylint: disable=W0201
        self._prior_tensor = prior                  # pylint: disable=W0201