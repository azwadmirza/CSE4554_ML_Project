def _parallel_amplitude(X, metric, metric_params, homology_dimensions, n_jobs):
    amplitude_func = implemented_amplitude_recipes[metric]
    effective_metric_params = metric_params.copy()
    none_dict = {dim: None for dim in homology_dimensions}
    samplings = effective_metric_params.pop("samplings", none_dict)
    step_sizes = effective_metric_params.pop("step_sizes", none_dict)

    amplitude_arrays = Parallel(n_jobs=n_jobs)(
        delayed(amplitude_func)(
            _subdiagrams(X[s], [dim], remove_dim=True),
            sampling=samplings[dim], step_size=step_sizes[dim],
            **effective_metric_params)
        for dim in homology_dimensions
        for s in gen_even_slices(_num_samples(X), effective_n_jobs(n_jobs)))

    amplitude_arrays = np.concatenate(amplitude_arrays).\
        reshape(len(homology_dimensions), len(X)).T

    return amplitude_arrays