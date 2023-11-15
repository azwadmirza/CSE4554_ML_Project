def get_video(video_path, subtitles_dir=None, subtitles=True, embedded_subtitles=None, release_name=None):
    """Returns the subliminal video for the given path

    :param video_path: the video path
    :type video_path: str
    :param subtitles_dir: the subtitles directory
    :type subtitles_dir: str
    :param subtitles: True if existing external subtitles should be taken into account
    :type subtitles: bool
    :param embedded_subtitles: True if embedded subtitles should be taken into account
    :type embedded_subtitles: bool
    :param release_name: the release name
    :type release_name: str
    :return: video
    :rtype: subliminal.video
    """
    key = video_key.format(video_path=video_path, subtitles_dir=subtitles_dir, subtitles=subtitles,
                           embedded_subtitles=embedded_subtitles, release_name=release_name)
    video = region.get(key, expiration_time=VIDEO_EXPIRATION_TIME)
    if video != NO_VALUE:
        logger.log(u'Found cached video information under key {0}'.format(key), logger.DEBUG)
        return video

    try:
        video_path = encode(video_path)
        subtitles_dir = encode(subtitles_dir or get_subtitles_dir(video_path))

        logger.log(u'Scanning video {0}...'.format(video_path), logger.DEBUG)
        video = scan_video(video_path)

        # external subtitles
        if subtitles:
            video.subtitle_languages |= set(search_external_subtitles(video_path, directory=subtitles_dir).values())

        if embedded_subtitles is None:
            embedded_subtitles = bool(not sickbeard.EMBEDDED_SUBTITLES_ALL and video_path.endswith('.mkv'))

        refine(video, episode_refiners=episode_refiners, embedded_subtitles=embedded_subtitles,
               release_name=release_name)

        region.set(key, video)
        logger.log(u'Video information cached under key {0}'.format(key), logger.DEBUG)

        return video
    except Exception as error:
        logger.log(u'Exception: {0}'.format(error), logger.DEBUG)