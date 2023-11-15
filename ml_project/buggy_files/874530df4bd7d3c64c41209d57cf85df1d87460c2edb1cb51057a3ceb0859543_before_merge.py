def validate_name(pattern, multi=None, anime_type=None,  # pylint: disable=too-many-arguments, too-many-return-statements
                  file_only=False, abd=False, sports=False):
    """
    See if we understand a name

    :param pattern: Name to analyse
    :param multi: Is this a multi-episode name
    :param anime_type: Is this anime
    :param file_only: Is this just a file or a dir
    :param abd: Is air-by-date enabled
    :param sports: Is this sports
    :return: True if valid name, False if not
    """
    ep = generate_sample_ep(multi, abd, sports, anime_type)

    new_name = ep.formatted_filename(pattern, multi, anime_type) + '.ext'
    new_path = ep.formatted_dir(pattern, multi)
    if not file_only:
        new_name = os.path.join(new_path, new_name)

    if not new_name:
        logger.log(u'Unable to create a name out of ' + pattern, logger.DEBUG)
        return False

    logger.log(u'Trying to parse ' + new_name, logger.DEBUG)

    try:
        parse_result = NameParser(series=ep.series, naming_pattern=True).parse(new_name)
    except (InvalidNameException, InvalidShowException) as error:
        logger.log(u'{}'.format(error), logger.DEBUG)
        return False

    logger.log(u'The name ' + new_name + ' parsed into ' + str(parse_result), logger.DEBUG)

    if abd or sports:
        if parse_result.air_date != ep.airdate:
            logger.log(u"Air date incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
    elif anime_type != 3:
        if parse_result.ab_episode_numbers and parse_result.ab_episode_numbers != [x.absolute_number
                                                                                   for x in [ep] + ep.related_episodes]:
            logger.log(u"Absolute numbering incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
    else:
        if parse_result.season_number != ep.season:
            logger.log(u"Season number incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False
        if parse_result.episode_numbers != [x.episode for x in [ep] + ep.related_episodes]:
            logger.log(u"Episode numbering incorrect in parsed episode, pattern isn't valid", logger.DEBUG)
            return False

    return True