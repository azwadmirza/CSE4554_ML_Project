def _groupby_indices(values):

    if is_categorical_dtype(values):

        # we have a categorical, so we can do quite a bit
        # bit better than factorizing again
        reverse = dict(enumerate(values.categories))
        codes = values.codes.astype('int64')
        _, counts = _hash.value_count_int64(codes, False)
    else:
        reverse, codes, counts = _algos.group_labels(
            _values_from_object(_ensure_object(values)))

    return _algos.groupby_indices(reverse, codes, counts)