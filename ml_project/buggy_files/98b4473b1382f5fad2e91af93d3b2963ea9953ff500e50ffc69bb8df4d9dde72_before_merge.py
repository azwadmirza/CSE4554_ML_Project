def _get_anidb_exceptions():
    anidb_exceptions = {}

    if should_refresh('anidb'):
        logger.log('Checking for scene exceptions updates from AniDB')

        for show in sickbeard.showList:
            if show.is_anime and show.indexer == 1:
                try:
                    anime = adba.Anime(None, name=show.name, tvdbid=show.indexerid, autoCorrectName=True)
                except Exception as error:
                    logger.log('Checking AniDB scene exceptions update failed for {0}. Error: {1}'.format
                               (show.name, error), logger.ERROR)
                    continue

                if anime and anime.name != show.name:
                    anidb_exceptions[text_type(show.indexerid)] = [{anime.name.decode('utf-8'): -1}]

        set_last_refresh('anidb')

    return anidb_exceptions