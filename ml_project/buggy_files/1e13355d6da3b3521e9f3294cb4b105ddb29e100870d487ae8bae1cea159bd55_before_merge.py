def get_scene_exceptions_by_name(show_name):
    """Look for a series_id, season and indexer for a given series scene exception."""
    # TODO: Rewrite to use exceptions_cache since there is no need to hit db.
    # TODO: Make the query more linient. For example. `Jojo's Bizarre Adventure Stardust Crusaders` will not match
    # while `Jojo's Bizarre Adventure - Stardust Crusaders` is available.
    # Try the obvious case first
    cache_db_con = db.DBConnection('cache.db')
    scene_exceptions = cache_db_con.select(
        b'SELECT indexer, indexer_id, season '
        b'FROM scene_exceptions '
        b'WHERE show_name = ? ORDER BY season ASC',
        [show_name])
    if scene_exceptions:
        # FIXME: Need to add additional layer indexer.
        return [(int(exception[b'indexer_id']), int(exception[b'season']), int(exception[b'indexer']))
                for exception in scene_exceptions]

    result = []
    scene_exceptions = cache_db_con.select(
        b'SELECT show_name, indexer, indexer_id, season '
        b'FROM scene_exceptions'
    )

    for exception in scene_exceptions:
        indexer = int(exception[b'indexer'])
        indexer_id = int(exception[b'indexer_id'])
        season = int(exception[b'season'])
        exception_name = exception[b'show_name']

        sanitized_name = helpers.sanitize_scene_name(exception_name)
        show_names = (
            exception_name.lower(),
            sanitized_name.lower().replace('.', ' '),
        )

        if show_name.lower() in show_names:
            logger.debug(
                'Scene exception lookup got indexer ID {cur_indexer},'
                ' using that', cur_indexer=indexer_id
            )
            result.append((indexer_id, season, indexer))

    return result or [(None, None, None)]