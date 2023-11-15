def update_network_dict():
    """Update timezone information from Medusa repositories."""

    logger.log(u'Started updating network timezones', logger.DEBUG)
    url = '{base_url}/sb_network_timezones/network_timezones.txt'.format(base_url=BASE_PYMEDUSA_URL)
    response = helpers.get_url(url, session=helpers.make_session(), returns='response')
    if not response or not response.text:
        logger.log(u'Updating network timezones failed, this can happen from time to time. URL: %s' % url, logger.WARNING)
        load_network_dict()
        return

    d = {}
    try:
        for line in response.text.splitlines():
            (key, val) = line.strip().rsplit(u':', 1)
            if key is None or val is None:
                continue
            d[key] = val
    except (IOError, OSError) as error:
        logger.log('Unable to build the network dictionary. Aborting update. Error: {error}'.format
                   (error=error), logger.WARNING)
        return

    cache_db_con = db.DBConnection('cache.db')

    network_list = dict(cache_db_con.select('SELECT * FROM network_timezones;'))

    queries = []
    for network, timezone in iteritems(d):
        existing = network in network_list
        if not existing:
            queries.append(['INSERT OR IGNORE INTO network_timezones VALUES (?,?);', [network, timezone]])
        elif network_list[network] != timezone:
            queries.append(['UPDATE OR IGNORE network_timezones SET timezone = ? WHERE network_name = ?;', [timezone, network]])

        if existing:
            del network_list[network]

    if network_list:
        purged = [x for x in network_list]
        queries.append(['DELETE FROM network_timezones WHERE network_name IN (%s);' % ','.join(['?'] * len(purged)), purged])

    if queries:
        cache_db_con.mass_action(queries)
        load_network_dict()

    logger.log(u'Finished updating network timezones', logger.DEBUG)