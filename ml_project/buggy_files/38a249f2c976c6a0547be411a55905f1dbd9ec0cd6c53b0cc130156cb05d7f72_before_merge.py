def download_best_subs(video_path, subtitles_dir, release_name, languages, subtitles=True, embedded_subtitles=True,
                       provider_pool=None):
    """Downloads the best subtitle for the given video

    :param video_path: the video path
    :type video_path: str
    :param subtitles_dir: the subtitles directory
    :type subtitles_dir: str
    :param release_name: the release name for the given video
    :type release_name: str
    :param languages: the needed languages
    :type languages: set of babelfish.Language
    :param subtitles: True if existing external subtitles should be taken into account
    :type subtitles: bool
    :param embedded_subtitles: True if embedded subtitles should be taken into account
    :type embedded_subtitles: bool
    :param provider_pool: provider pool to be used
    :type provider_pool: subliminal.ProviderPool
    :return: the downloaded subtitles
    :rtype:
    """
    try:
        video = get_video(video_path, subtitles_dir=subtitles_dir, subtitles=subtitles,
                          embedded_subtitles=embedded_subtitles, release_name=release_name)

        if not video:
            logger.log(u'Exception caught in subliminal.scan_video for {0}'.format(video_path), logger.DEBUG)
            return list()

        pool = provider_pool or get_provider_pool()

        if sickbeard.SUBTITLES_PRE_SCRIPTS:
            run_subs_pre_scripts(video_path)

        subtitles_list = pool.list_subtitles(video, languages)
        for provider in pool.providers:
            if provider in pool.discarded_providers:
                logger.log(u'Could not search in {0} provider. Discarding for now'.format(provider), logger.DEBUG)

        if not subtitles_list:
            logger.log(u'No subtitles found for {0}'.format(video_path))
            return list()

        min_score = get_min_score()
        scored_subtitles = sorted([(s, compute_score(s, video, hearing_impaired=sickbeard.SUBTITLES_HEARING_IMPAIRED))
                                  for s in subtitles_list], key=operator.itemgetter(1), reverse=True)
        for subtitle, score in scored_subtitles:
            logger.log(u'[{0:>13s}:{1:<5s}] score = {2:3d}/{3:3d} for {4}'.format
                       (subtitle.provider_name, subtitle.language, score, min_score,
                        get_subtitle_description(subtitle)), logger.DEBUG)

        found_subtitles = pool.download_best_subtitles(subtitles_list, video, languages=languages,
                                                       hearing_impaired=sickbeard.SUBTITLES_HEARING_IMPAIRED,
                                                       min_score=min_score, only_one=not sickbeard.SUBTITLES_MULTI)

        if not found_subtitles:
            logger.log(u'No subtitles found for {0} with min_score {1}'.format(video_path, min_score))
            return list()

        save_subtitles(video, found_subtitles, directory=subtitles_dir, single=not sickbeard.SUBTITLES_MULTI)

        for subtitle in found_subtitles:
            logger.log(u'Found subtitle for {0} in {1} provider with language {2}'.format
                       (video_path, subtitle.provider_name, subtitle.language.opensubtitles), logger.INFO)
            subtitle_path = compute_subtitle_path(subtitle, video_path, subtitles_dir)

            sickbeard.helpers.chmodAsParent(subtitle_path)
            sickbeard.helpers.fixSetGroupID(subtitle_path)

        return found_subtitles
    except IOError as error:
        if 'No space left on device' in ex(error):
            logger.log(u'Not enough space on the drive to save subtitles', logger.WARNING)
        else:
            logger.log(traceback.format_exc(), logger.WARNING)
    except Exception as error:
        logger.log(u'Exception: {0}'.format(error), logger.DEBUG)
        logger.log(u'Error occurred when downloading subtitles for: {0}'.format(video_path))
        logger.log(traceback.format_exc(), logger.ERROR)

    return list()