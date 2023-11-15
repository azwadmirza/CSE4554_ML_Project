def extract_distinct_params(exps_data,
                            excluded_params=('exp_name', 'seed', 'log_dir'),
                            length=1):
    # all_pairs = unique(flatten([d.flat_params.items() for d in exps_data]))
    # if logger:
    #     logger("(Excluding {excluded})".format(
    #       excluded=', '.join(excluded_params)))
    # def cmp(x,y):
    #     if x < y:
    #         return -1
    #     elif x > y:
    #         return 1
    #     else:
    #         return 0

    try:
        stringified_pairs = sorted(
            map(
                eval,
                unique(
                    flatten([
                        list(map(smart_repr, list(d.flat_params.items())))
                        for d in exps_data
                    ]))),
            key=lambda x: (tuple(0. if it is None else it for it in x), ))
    except Exception as e:
        print(e)
    proposals = [
        (k, [x[1] for x in v])
        for k, v in itertools.groupby(stringified_pairs, lambda x: x[0])
    ]
    filtered = [(k, v) for (k, v) in proposals if len(v) > length and all(
        [k.find(excluded_param) != 0 for excluded_param in excluded_params])]
    return filtered