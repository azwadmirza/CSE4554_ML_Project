def subtitles_enabled(*args):
    """Try to parse names to a show and check whether the show has subtitles enabled.

    :param args:
    :return:
    :rtype: bool
    """
    for name in args:
        try:
            parse_result = NameParser().parse(name, cache_result=True)
            if parse_result.show.indexerid:
                main_db_con = db.DBConnection()
                sql_results = main_db_con.select("SELECT subtitles FROM tv_shows WHERE indexer_id = ? LIMIT 1",
                                                 [parse_result.show.indexerid])
                return bool(sql_results[0]["subtitles"]) if sql_results else False

            logger.log(u'Empty indexer ID for: {name}'.format(name=name), logger.WARNING)
        except (InvalidNameException, InvalidShowException):
            logger.log(u'Not enough information to parse filename into a valid show. Consider adding scene exceptions '
                       u'or improve naming for: {name}'.format(name=name), logger.WARNING)
    return False