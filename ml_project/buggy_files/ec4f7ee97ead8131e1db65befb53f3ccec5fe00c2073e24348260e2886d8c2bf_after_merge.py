def _parallel_pairwise(X1, X2, metric, metric_params,
                       homology_dimensions, n_jobs):
    metric_func = implemented_metric_recipes[metric]
    effective_metric_params = metric_params.copy()
    none_dict = {dim: None for dim in homology_dimensions}
    samplings = effective_metric_params.pop("samplings", none_dict)
    step_sizes = effective_metric_params.pop("step_sizes", none_dict)

    if X2 is None:
        X2 = X1

    n_columns = len(X2)
    distance_matrices = Parallel(n_jobs=n_jobs)(
        delayed(metric_func)(_subdiagrams(X1, [dim], remove_dim=True),
                             _subdiagrams(X2[s], [dim], remove_dim=True),
                             sampling=samplings[dim],
                             step_size=step_sizes[dim],
                             **effective_metric_params)
        for dim in homology_dimensions
        for s in gen_even_slices(n_columns, effective_n_jobs(n_jobs)))

    distance_matrices = np.concatenate(distance_matrices, axis=1)
    distance_matrices = np.stack(
        [distance_matrices[:, i * n_columns:(i + 1) * n_columns]
         for i in range(len(homology_dimensions))],
        axis=2)
    return distance_matrices