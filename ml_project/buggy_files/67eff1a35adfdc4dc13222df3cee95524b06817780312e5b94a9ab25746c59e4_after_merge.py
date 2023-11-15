def _get_codes_for_values(values, categories):
    """
    utility routine to turn values into codes given the specified categories
    """
    from pandas.core.algorithms import _get_data_algo, _hashtables
    if is_dtype_equal(values.dtype, categories.dtype):
        # To prevent erroneous dtype coercion in _get_data_algo, retrieve
        # the underlying numpy array. gh-22702
        values = getattr(values, 'values', values)
        categories = getattr(categories, 'values', categories)
    else:
        values = ensure_object(values)
        categories = ensure_object(categories)

    (hash_klass, vec_klass), vals = _get_data_algo(values, _hashtables)
    (_, _), cats = _get_data_algo(categories, _hashtables)
    t = hash_klass(len(cats))
    t.map_locations(cats)
    return coerce_indexer_dtype(t.lookup(vals), cats)