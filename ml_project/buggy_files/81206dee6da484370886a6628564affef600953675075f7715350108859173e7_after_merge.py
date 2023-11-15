def _expand_parameters(circuits, run_config):
    """Verifies that there is a single common set of parameters shared between
    all circuits and all parameter binds in the run_config. Returns an expanded
    list of circuits (if parameterized) with all parameters bound, and a copy of
    the run_config with parameter_binds cleared.

    If neither the circuits nor the run_config specify parameters, the two are
    returned unmodified.

    Raises:
        QiskitError: if run_config parameters are not compatible with circuit parameters

    Returns:
        Tuple(List[QuantumCircuit], RunConfig):
          - List of input circuits expanded and with parameters bound
          - RunConfig with parameter_binds removed
    """

    parameter_binds = run_config.parameter_binds

    if parameter_binds or \
       any(circuit.parameters for circuit in circuits):

        # Unroll params here in order to handle ParamVects
        all_bind_parameters = [QuantumCircuit()._unroll_param_dict(bind).keys()
                               for bind in parameter_binds]

        all_circuit_parameters = [circuit.parameters for circuit in circuits]

        # Collect set of all unique parameters across all circuits and binds
        unique_parameters = {param
                             for param_list in all_bind_parameters + all_circuit_parameters
                             for param in param_list}

        # Check that all parameters are common to all circuits and binds
        if not all_bind_parameters \
           or not all_circuit_parameters \
           or any(unique_parameters != bind_params for bind_params in all_bind_parameters) \
           or any(unique_parameters != parameters for parameters in all_circuit_parameters):
            raise QiskitError(
                ('Mismatch between run_config.parameter_binds and all circuit parameters. ' +
                 'Parameter binds: {} ' +
                 'Circuit parameters: {}').format(all_bind_parameters, all_circuit_parameters))

        circuits = [circuit.bind_parameters(binds)
                    for circuit in circuits
                    for binds in parameter_binds]

        # All parameters have been expanded and bound, so remove from run_config
        run_config = copy.deepcopy(run_config)
        run_config.parameter_binds = []

    return circuits, run_config