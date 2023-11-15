def default_pass_manager(basis_gates, coupling_map, initial_layout, seed_mapper):
    """
    The default pass manager that maps to the coupling map.

    Args:
        basis_gates (list[str]): list of basis gate names supported by the
            target. Default: ['u1','u2','u3','cx','id']
        initial_layout (Layout or None): If None, trivial layout will be chosen.
        coupling_map (CouplingMap): coupling map (perhaps custom) to target
            in mapping.
        seed_mapper (int or None): random seed for the swap_mapper.

    Returns:
        PassManager: A pass manager to map and optimize.
    """
    pass_manager = PassManager()
    pass_manager.property_set['layout'] = initial_layout

    pass_manager.append(Unroller(basis_gates))

    # Use the trivial layout if no layouto is found
    pass_manager.append(TrivialLayout(coupling_map),
                        condition=lambda property_set: not property_set['layout'])

    # if the circuit and layout already satisfy the coupling_constraints, use that layout
    # otherwise layout on the most densely connected physical qubit subset
    pass_manager.append(CheckMap(coupling_map))
    pass_manager.append(DenseLayout(coupling_map),
                        condition=lambda property_set: not property_set['is_swap_mapped'])

    # Extend and enlarge the the dag/layout with ancillas using the full coupling map
    pass_manager.append(ExtendLayout(coupling_map))
    pass_manager.append(EnlargeWithAncilla())

    # Swap mapper
    pass_manager.append(LegacySwap(coupling_map, trials=20, seed=seed_mapper))

    # Expand swaps
    pass_manager.append(Decompose(SwapGate))

    # Change CX directions
    pass_manager.append(CXDirection(coupling_map))

    # Unroll to the basis
    pass_manager.append(Unroller(['u1', 'u2', 'u3', 'id', 'cx']))

    # Simplify single qubit gates and CXs
    pass_manager.append([Optimize1qGates(), CXCancellation(), Depth(), FixedPoint('depth')],
                        do_while=lambda property_set: not property_set['depth_fixed_point'])
    return pass_manager