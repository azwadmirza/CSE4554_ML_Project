def _cost(config, run_history, instance_seed_pairs=None):
    """Return array of all costs for the given config for further calculations.

    Parameters
    ----------
    config : Configuration
        configuration to calculate objective for
    run_history : RunHistory
        RunHistory object from which the objective value is computed.
    instance_seed_pairs : list, optional (default=None)
        list of tuples of instance-seeds pairs. If None, the run_history is
        queried for all runs of the given configuration.

    Returns
    ----------
    list
    """
    try:
        id_ = run_history.config_ids[config.__repr__()]
    except KeyError:  # challenger was not running so far
        return []

    if instance_seed_pairs is None:
        instance_seed_pairs = run_history.get_runs_for_config(config)

    costs = []
    for i, r in instance_seed_pairs:
        k = run_history.RunKey(id_, i, r)
        costs.append(run_history.data[k].cost)
    return costs