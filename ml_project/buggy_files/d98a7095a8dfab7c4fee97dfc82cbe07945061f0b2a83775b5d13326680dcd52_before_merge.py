    def assign_parameters(self, param_dict, inplace=False):
        """Assign parameters to new parameters or values.

        The keys of the parameter dictionary must be Parameter instances in the current circuit. The
        values of the dictionary can either be numeric values or new parameter objects.
        The values can be assigned to the current circuit object or to a copy of it.

        Args:
            param_dict (dict): A dictionary specifying the mapping from ``current_parameter``
                to ``new_parameter``, where ``new_parameter`` can be a new parameter object
                or a numeric value.
            inplace (bool): If False, a copy of the circuit with the bound parameters is
                returned. If True the circuit instance itself is modified.

        Raises:
            CircuitError: If param_dict contains parameters not present in the circuit

        Returns:
            Optional(QuantumCircuit): A copy of the circuit with bound parameters, if
            ``inplace`` is True, otherwise None.

        Examples:

            Create a parameterized circuit and assign the parameters in-place.

            .. jupyter-execute::

                from qiskit.circuit import QuantumCircuit, Parameter

                circuit = QuantumCircuit(2)
                params = [Parameter('A'), Parameter('B'), Parameter('C')]
                circuit.ry(params[0], 0)
                circuit.crx(params[1], 0, 1)

                print('Original circuit:')
                print(circuit.draw())

                circuit.assign_parameters({params[0]: params[2]}, inplace=True)

                print('Assigned in-place:')
                print(circuit.draw())

            Bind the values out-of-place and get a copy of the original circuit.

            .. jupyter-execute::

                from qiskit.circuit import QuantumCircuit, ParameterVector

                circuit = QuantumCircuit(2)
                params = ParameterVector('P', 2)
                circuit.ry(params[0], 0)
                circuit.crx(params[1], 0, 1)

                bound_circuit = circuit.assign_parameters({params[0]: 1, params[1]: 2})
                print('Bound circuit:')
                print(bound_circuit.draw())

                print('The original circuit is unchanged:')
                print(circuit.draw())

        """
        # replace in self or in a copy depending on the value of in_place
        bound_circuit = self if inplace else self.copy()

        # unroll the parameter dictionary (needed if e.g. it contains a ParameterVector)
        unrolled_param_dict = self._unroll_param_dict(param_dict)

        # check that only existing parameters are in the parameter dictionary
        if unrolled_param_dict.keys() > self._parameter_table.keys():
            raise CircuitError('Cannot bind parameters ({}) not present in the circuit.'.format(
                [str(p) for p in param_dict.keys() - self._parameter_table]))

        # replace the parameters with a new Parameter ("substitute") or numeric value ("bind")
        for parameter, value in unrolled_param_dict.items():
            bound_circuit._assign_parameter(parameter, value)

        return None if inplace else bound_circuit