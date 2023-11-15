def validate_show(show, season=None, episode=None):
    """Reindex show from originating indexer, and return indexer information for the passed episode."""
    from medusa.indexers.indexer_api import indexerApi
    from medusa.indexers.indexer_exceptions import IndexerEpisodeNotFound, IndexerSeasonNotFound, IndexerShowNotFound
    indexer_lang = show.lang

    try:
        indexer_api_params = indexerApi(show.indexer).api_params.copy()

        if indexer_lang and not indexer_lang == app.INDEXER_DEFAULT_LANGUAGE:
            indexer_api_params['language'] = indexer_lang

        if show.dvd_order != 0:
            indexer_api_params['dvdorder'] = True

        if season is None and episode is None:
            return show.indexer_api

        return show.indexer_api[show.indexerid][season][episode]
    except (IndexerEpisodeNotFound, IndexerSeasonNotFound, IndexerShowNotFound) as error:
        log.debug(u'Unable to validate show. Reason: {0!r}', error.message)
        pass