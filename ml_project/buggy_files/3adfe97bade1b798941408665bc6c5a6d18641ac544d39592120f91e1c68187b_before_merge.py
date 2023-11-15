def _bin(X, metric, n_bins=100, **kw_args):
    homology_dimensions = sorted(list(set(X[0, :, 2])))
    # For some vectorizations, we force the values to be the same + widest
    sub_diags = {dim: _subdiagrams(X, [dim], remove_dim=True)
                 for dim in homology_dimensions}
    # For persistence images, move into birth-persistence
    if metric == 'persistence_image':
        for dim in homology_dimensions:
            sub_diags[dim][:, :, [1]] = sub_diags[dim][:, :, [1]] \
                - sub_diags[dim][:, :, [0]]
    min_vals = {dim: np.min(sub_diags[dim], axis=(0, 1))
                for dim in homology_dimensions}
    max_vals = {dim: np.max(sub_diags[dim], axis=(0, 1))
                for dim in homology_dimensions}

    if metric in ['landscape', 'betti', 'heat', 'silhouette']:
        #  Taking the min(resp. max) of a tuple `m` amounts to extracting
        #  the birth (resp. death) value
        min_vals = {d: np.array(2*[np.min(m)]) for d, m in min_vals.items()}
        max_vals = {d: np.array(2*[np.max(m)]) for d, m in max_vals.items()}

    # Scales between axes should be kept the same, but not between dimension
    all_max_values = np.stack(list(max_vals.values()))
    if len(homology_dimensions) == 1:
        all_max_values = all_max_values.reshape(1, -1)
    global_max_val = np.max(all_max_values, axis=0)
    max_vals = {dim: np.array([max_vals[dim][k] if
                               (max_vals[dim][k] != min_vals[dim][k])
                               else global_max_val[k] for k in range(2)])
                for dim in homology_dimensions}

    samplings = {}
    step_sizes = {}
    for dim in homology_dimensions:
        samplings[dim], step_sizes[dim] = np.linspace(min_vals[dim],
                                                      max_vals[dim],
                                                      retstep=True,
                                                      num=n_bins)
    if metric in ['landscape', 'betti', 'heat', 'silhouette']:
        for dim in homology_dimensions:
            samplings[dim] = samplings[dim][:, [0], None]
            step_sizes[dim] = step_sizes[dim][0]
    return samplings, step_sizes