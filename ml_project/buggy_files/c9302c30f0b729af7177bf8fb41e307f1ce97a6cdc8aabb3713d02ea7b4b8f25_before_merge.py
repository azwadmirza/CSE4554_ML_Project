def value_counts(values, sort=True, ascending=False):
    """
    Compute a histogram of the counts of non-null values

    Returns
    -------
    value_counts : Series
    """
    from collections import defaultdict
    if com.is_integer_dtype(values.dtype):
        values = com._ensure_int64(values)
        keys, counts = lib.value_count_int64(values)
        result = Series(counts, index=keys)
    else:
        counter = defaultdict(lambda: 0)
        values = values[com.notnull(values)]
        for value in values:
            counter[value] += 1
        result = Series(counter)

    if sort:
        result.sort()
        if not ascending:
            result = result[::-1]

    return result