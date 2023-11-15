def qaoa_ansatz(gammas, betas):
    """
    Function that returns a QAOA ansatz program for a list of angles betas and gammas. len(betas) ==
    len(gammas) == P for a QAOA program of order P.

    :param list(float) gammas: Angles over which to parameterize the cost Hamiltonian.
    :param list(float) betas: Angles over which to parameterize the driver Hamiltonian.
    :return: The QAOA ansatz program.
    :rtype: Program.
    """
    return Program([exponentiate_commuting_pauli_sum(h_cost)(g)
                    + exponentiate_commuting_pauli_sum(h_driver)(b)
                    for g, b in zip(gammas, betas)])