def _get_anidb_exceptions(force):
    anidb_exceptions = defaultdict(dict)
    # AniDB exceptions use TVDB as indexer
    exceptions = anidb_exceptions[INDEXER_TVDBV2]

    if force or should_refresh('anidb'):
        logger.info('Checking for scene exceptions updates from AniDB')

        for show in app.showList:
            if all([show.name, show.is_anime, show.indexer == INDEXER_TVDBV2]):
                try:
                    anime = adba.Anime(
                        None,
                        name=show.name,
                        tvdbid=show.indexerid,
                        autoCorrectName=True,
                        cache_path=join(app.CACHE_DIR, 'adba')
                    )
                except ValueError as error:
                    logger.debug(
                        "Couldn't update scene exceptions for {show},"
                        " AniDB doesn't have this show. Error: {msg}", {'show': show.name, 'msg': error}
                    )
                    continue
                except Exception as error:
                    logger.error(
                        'Checking AniDB scene exceptions update failed'
                        ' for {show}. Error: {msg}', {'show': show.name, 'msg': error}
                    )
                    continue

                if anime and anime.name != show.name:
                    series_id = int(show.series_id)
                    exceptions[series_id] = [{anime.name.decode('utf-8'): -1}]

        set_last_refresh('anidb')

    return anidb_exceptions