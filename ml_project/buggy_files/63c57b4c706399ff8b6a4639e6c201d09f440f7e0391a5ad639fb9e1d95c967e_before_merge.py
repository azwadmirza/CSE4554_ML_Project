def get_all_recommended_series_from_cache(indexers):
    """
    Retrieve all recommended show objects from the dogpile cache for a specific indexer or a number of indexers.

    For example: `get_all_recommended_series_from_cache(['imdb', 'anidb'])` will return all recommended show objects, for the
    indexers imdb and anidb.

    :param indexers: indexer or list of indexers. Indexers need to be passed as a string. For example: 'imdb', 'anidb' or 'trakt'.
    :return: List of recommended show objects.
    """
    indexers = ensure_list(indexers)
    all_series = []
    for indexer in indexers:
        index = recommended_series_cache.get(binary_type(indexer))
        if not index:
            continue

        for index_item in index:
            key = '{indexer}_{series_id}'.format(indexer=indexer, series_id=index_item)
            series = recommended_series_cache.get(binary_type(key))
            if series:
                all_series.append(series)

    return all_series