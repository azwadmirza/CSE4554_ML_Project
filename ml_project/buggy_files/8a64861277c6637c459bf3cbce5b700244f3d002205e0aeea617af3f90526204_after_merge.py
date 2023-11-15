    def _build(self):
        unconstrained = self._build_parameter()
        constrained = self._build_constrained(unconstrained)
        prior = self._build_prior(unconstrained, constrained)

        self._is_initialized_tensor = tf.is_variable_initialized(unconstrained)
        self._unconstrained_tensor = unconstrained
        self._constrained_tensor = constrained
        self._prior_tensor = prior