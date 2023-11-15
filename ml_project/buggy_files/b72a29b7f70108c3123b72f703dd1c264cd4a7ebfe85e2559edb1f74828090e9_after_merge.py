    def parameters(self):
        """Convenience function to get the parameters defined in the parameter table."""
        # parameters from gates
        params = self._parameter_table.get_keys()

        # parameters in global phase
        if isinstance(self.global_phase, ParameterExpression):
            return params.union(self.global_phase.parameters)

        return params