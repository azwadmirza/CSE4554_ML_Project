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
    hash_klass, values = _get_data_algo(values, _hashtables)

    uniques = []
    table = hash_klass(len(values))
    labels, counts = table.get_labels(values, uniques, 0, na_sentinel)

    uniques = com._asarray_tuplesafe(uniques)
    if sort and len(counts) > 0:
        sorter = uniques.argsort()
        reverse_indexer = np.empty(len(sorter), dtype=np.int32)
        reverse_indexer.put(sorter, np.arange(len(sorter)))

        mask = labels < 0
        labels = reverse_indexer.take(labels)
        np.putmask(labels, mask, -1)

        uniques = uniques.take(sorter)
        counts = counts.take(sorter)

    return labels, uniques, counts