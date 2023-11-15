def factorize(values, sort=False, order=None, na_sentinel=-1):
    """
    Encode input values as an enumerated type or categorical variable

    Parameters
    ----------
    values : sequence
    sort :
    order :

    Returns
    -------
    """
    values = np.asarray(values)
    is_datetime = com.is_datetime64_dtype(values)
    hash_klass, values = _get_data_algo(values, _hashtables)

    uniques = []
    table = hash_klass(len(values))
    labels, counts = table.get_labels(values, uniques, 0, na_sentinel)

    labels = com._ensure_platform_int(labels)

    uniques = com._asarray_tuplesafe(uniques)
    if sort and len(counts) > 0:
        sorter = uniques.argsort()
        reverse_indexer = np.empty(len(sorter), dtype=np.int_)
        reverse_indexer.put(sorter, np.arange(len(sorter)))

        mask = labels < 0
        labels = reverse_indexer.take(labels)
        np.putmask(labels, mask, -1)

        uniques = uniques.take(sorter)
        counts = counts.take(sorter)

    if is_datetime:
        uniques = np.array(uniques, dtype='M8[ns]')

    return labels, uniques, counts