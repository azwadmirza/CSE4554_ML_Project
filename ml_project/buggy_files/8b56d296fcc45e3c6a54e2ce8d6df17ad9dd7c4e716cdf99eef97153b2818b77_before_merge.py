    def _assign_parameter(self, parameter, value):
        """Update this circuit where instances of ``parameter`` are replaced by ``value``, which
        can be either a numeric value or a new parameter expression.

        Args:
            parameter (ParameterExpression): Parameter to be bound
            value (Union(ParameterExpression, float, int)): A numeric or parametric expression to
                replace instances of ``parameter``.
        """
        for instr, param_index in self._parameter_table[parameter]:
            new_param = instr.params[param_index].assign(parameter, value)
            # if fully bound, validate
            if len(new_param.parameters) == 0:
                instr.params[param_index] = instr.validate_parameter(new_param)
            else:
                instr.params[param_index] = new_param

            self._rebind_definition(instr, parameter, value)

        if isinstance(value, ParameterExpression):
            entry = self._parameter_table.pop(parameter)
            for new_parameter in value.parameters:
                if new_parameter in self._parameter_table:
                    self._parameter_table[new_parameter].extend(entry)
                else:
                    self._parameter_table[new_parameter] = entry
        else:
            del self._parameter_table[parameter]  # clear evaluated expressions

        if (isinstance(self.global_phase, ParameterExpression) and
                parameter in self.global_phase.parameters):
            self.global_phase = self.global_phase.assign(parameter, value)
        self._assign_calibration_parameters(parameter, value)