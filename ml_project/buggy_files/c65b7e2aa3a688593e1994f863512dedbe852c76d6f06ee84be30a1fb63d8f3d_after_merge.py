    def _append(self, instruction, qargs, cargs):
        """Append an instruction to the end of the circuit, modifying
        the circuit in place.

        Args:
            instruction (Instruction or Operator): Instruction instance to append
            qargs (list(tuple)): qubits to attach instruction to
            cargs (list(tuple)): clbits to attach instruction to

        Returns:
            Instruction: a handle to the instruction that was just added

        Raises:
            QiskitError: if the gate is of a different shape than the wires
                it is being attached to.
        """
        if not isinstance(instruction, Instruction):
            raise QiskitError('object is not an Instruction.')

        # do some compatibility checks
        self._check_dups(qargs)
        self._check_qargs(qargs)
        self._check_cargs(cargs)

        # add the instruction onto the given wires
        instruction_context = instruction, qargs, cargs
        self.data.append(instruction_context)

        # track variable parameters in instruction
        for param_index, param in enumerate(instruction.params):
            if isinstance(param, ParameterExpression):
                current_parameters = self.parameters

                for parameter in param.parameters:
                    if parameter in current_parameters:
                        if not self._check_dup_param_spec(self._parameter_table[parameter],
                                                          instruction, param_index):
                            self._parameter_table[parameter].append((instruction, param_index))
                    else:
                        if parameter.name in {p.name for p in current_parameters}:
                            raise QiskitError(
                                'Name conflict on adding parameter: {}'.format(parameter.name))
                        self._parameter_table[parameter] = [(instruction, param_index)]

        return instruction