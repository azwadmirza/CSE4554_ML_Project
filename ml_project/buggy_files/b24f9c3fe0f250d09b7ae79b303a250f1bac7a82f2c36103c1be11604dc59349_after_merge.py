def download_best_subs(video_path, subtitles_dir, release_name, languages, subtitles=True, embedded_subtitles=True,
                       provider_pool=None):
    """Download the best subtitle for the given video.

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
    :rtype: list of subliminal.subtitle.Subtitle
    """
    try:
        video = get_video(video_path, subtitles_dir=subtitles_dir, subtitles=subtitles,
                          embedded_subtitles=embedded_subtitles, release_name=release_name)

        if not video:
            logger.info(u'Exception caught in subliminal.scan_video for %s', video_path)
            return []

        pool = provider_pool or get_provider_pool()

        if sickbeard.SUBTITLES_PRE_SCRIPTS:
            run_subs_pre_scripts(video_path)

        subtitles_list = pool.list_subtitles(video, languages)
        for provider in pool.providers:
            if provider in pool.discarded_providers:
                logger.debug(u'Could not search in %s provider. Discarding for now', provider)

        if not subtitles_list:
            logger.info(u'No subtitles found for %s', video_path)
            return []

        min_score = get_min_score()
        scored_subtitles = sorted([(s, compute_score(s, video, hearing_impaired=sickbeard.SUBTITLES_HEARING_IMPAIRED))
                                  for s in subtitles_list], key=operator.itemgetter(1), reverse=True)
        for subtitle, score in scored_subtitles:
            logger.debug(u'[{0:>13s}:{1:<5s}] score = {2:3d}/{3:3d} for {4}'.format(
                subtitle.provider_name, subtitle.language, score, min_score, get_subtitle_description(subtitle)))

        found_subtitles = pool.download_best_subtitles(subtitles_list, video, languages=languages,
                                                       hearing_impaired=sickbeard.SUBTITLES_HEARING_IMPAIRED,
                                                       min_score=min_score, only_one=not sickbeard.SUBTITLES_MULTI)

        if not found_subtitles:
            logger.info(u'No subtitles found for %s with min_score %d', video_path, min_score)
            return []

        save_subtitles(video, found_subtitles, directory=_encode(subtitles_dir), single=not sickbeard.SUBTITLES_MULTI)

        for subtitle in found_subtitles:
            logger.info(u'Found subtitle for %s in %s provider with language %s', video_path, subtitle.provider_name,
                        subtitle.language.opensubtitles)
            subtitle_path = compute_subtitle_path(subtitle, video_path, subtitles_dir)

            sickbeard.helpers.chmodAsParent(subtitle_path)
            sickbeard.helpers.fixSetGroupID(subtitle_path)

        return found_subtitles
    except IOError as error:
        if 'No space left on device' in ex(error):
            logger.warning(u'Not enough space on the drive to save subtitles')
        else:
            logger.warning(traceback.format_exc())
    except Exception as error:
        logger.debug(u'Exception: %s', error)
        logger.info(u'Error occurred when downloading subtitles for: %s', video_path)
        logger.error(traceback.format_exc())

    return []