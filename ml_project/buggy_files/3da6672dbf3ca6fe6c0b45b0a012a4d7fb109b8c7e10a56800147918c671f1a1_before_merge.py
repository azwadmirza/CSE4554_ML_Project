def merge_dicts(
        dicts: Sequence[Mapping],
        agg_key_funcs: Optional[Mapping[str, Callable[[Sequence[float]], float]]] = None,
        default_func: Callable[[Sequence[float]], float] = np.mean
) -> Dict:
    """
    Merge a sequence with dictionaries into one dictionary by aggregating the
    same keys with some given function.

    Args:
        dicts:
            Sequence of dictionaries to be merged.
        agg_key_funcs:
            Mapping from key name to function. This function will aggregate a
            list of values, obtained from the same key of all dictionaries.
            If some key has no specified aggregation function, the default one
            will be used. Default is: ``None`` (all keys will be aggregated by the
            default function).
        default_func:
            Default function to aggregate keys, which are not presented in the
            `agg_key_funcs` map.

    Returns:
        Dictionary with merged values.

    Examples:
        >>> import pprint
        >>> d1 = {'a': 1.7, 'b': 2.0, 'c': 1}
        >>> d2 = {'a': 1.1, 'b': 2.2, 'v': 1}
        >>> d3 = {'a': 1.1, 'v': 2.3}
        >>> dflt_func = min
        >>> agg_funcs = {'a': np.mean, 'v': max}
        >>> pprint.pprint(merge_dicts([d1, d2, d3], agg_funcs, dflt_func))
        {'a': 1.3, 'b': 2.0, 'c': 1, 'v': 2.3}
    """

    keys = list(functools.reduce(operator.or_, [set(d.keys()) for d in dicts]))
    d_out = {}
    for k in keys:
        fn = agg_key_funcs.get(k, default_func) if agg_key_funcs else default_func
        agg_val = fn([v for v in [d_in.get(k) for d_in in dicts] if v is not None])
        d_out[k] = agg_val

    return d_out