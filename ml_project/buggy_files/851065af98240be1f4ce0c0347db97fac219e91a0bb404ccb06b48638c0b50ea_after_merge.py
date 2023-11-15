def print_summary(samples, prob=0.9, group_by_chain=True):
    """
    Prints a summary table displaying diagnostics of ``samples`` from the
    posterior. The diagnostics displayed are mean, standard deviation, median,
    the 90% Credibility Interval, :func:`~pyro.ops.stats.effective_sample_size`,
    :func:`~pyro.ops.stats.split_gelman_rubin`.

    :param dict samples: dictionary of samples keyed by site name.
    :param float prob: the probability mass of samples within the credibility interval.
    :param bool group_by_chain: If True, each variable in `samples`
        will be treated as having shape `num_chains x num_samples x sample_shape`.
        Otherwise, the corresponding shape will be `num_samples x sample_shape`
        (i.e. without chain dimension).
    """
    if len(samples) == 0:
        return
    summary_dict = summary(samples, prob, group_by_chain)

    row_names = {k: k + '[' + ','.join(map(lambda x: str(x - 1), v.shape[2:])) + ']'
                 for k, v in samples.items()}
    max_len = max(max(map(lambda x: len(x), row_names.values())), 10)
    name_format = '{:>' + str(max_len) + '}'
    header_format = name_format + ' {:>9}' * 7
    columns = [''] + list(list(summary_dict.values())[0].keys())

    print()
    print(header_format.format(*columns))

    row_format = name_format + ' {:>9.2f}' * 7
    for name, stats_dict in summary_dict.items():
        shape = stats_dict["mean"].shape
        if len(shape) == 0:
            print(row_format.format(name, *stats_dict.values()))
        else:
            for idx in product(*map(range, shape)):
                idx_str = '[{}]'.format(','.join(map(str, idx)))
                print(row_format.format(name + idx_str, *[v[idx] for v in stats_dict.values()]))
    print()