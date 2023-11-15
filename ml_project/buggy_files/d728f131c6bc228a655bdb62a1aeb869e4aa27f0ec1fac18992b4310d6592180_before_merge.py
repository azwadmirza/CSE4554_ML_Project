def Concurrently(ops: List[LocalIterator],
                 *,
                 mode="round_robin",
                 output_indexes=None,
                 round_robin_weights=None):
    """Operator that runs the given parent iterators concurrently.

    Args:
        mode (str): One of {'round_robin', 'async'}.
            - In 'round_robin' mode, we alternate between pulling items from
              each parent iterator in order deterministically.
            - In 'async' mode, we pull from each parent iterator as fast as
              they are produced. This is non-deterministic.
        output_indexes (list): If specified, only output results from the
            given ops. For example, if output_indexes=[0], only results from
            the first op in ops will be returned.
        round_robin_weights (list): List of weights to use for round robin
            mode. For example, [2, 1] will cause the iterator to pull twice
            as many items from the first iterator as the second. [2, 1, *] will
            cause as many items to be pulled as possible from the third
            iterator without blocking. This is only allowed in round robin
            mode.

        >>> sim_op = ParallelRollouts(...).for_each(...)
        >>> replay_op = LocalReplay(...).for_each(...)
        >>> combined_op = Concurrently([sim_op, replay_op], mode="async")
    """

    if len(ops) < 2:
        raise ValueError("Should specify at least 2 ops.")
    if mode == "round_robin":
        deterministic = True
    elif mode == "async":
        deterministic = False
        if round_robin_weights:
            raise ValueError(
                "round_robin_weights cannot be specified in async mode")
    else:
        raise ValueError("Unknown mode {}".format(mode))
    if round_robin_weights and all(r == "*" for r in round_robin_weights):
        raise ValueError("Cannot specify all round robin weights = *")

    if output_indexes:
        for i in output_indexes:
            assert i in range(len(ops)), ("Index out of range", i)

        def tag(op, i):
            return op.for_each(lambda x: (i, x))

        ops = [tag(op, i) for i, op in enumerate(ops)]

    output = ops[0].union(
        *ops[1:],
        deterministic=deterministic,
        round_robin_weights=round_robin_weights)

    if output_indexes:
        output = (output.filter(lambda tup: tup[0] in output_indexes)
                  .for_each(lambda tup: tup[1]))

    return output