def invalidate_video_cache(video_path):
    """Invalidate the cached subliminal.video.Video for the specified path.

    :param video_path: the video path
    :type video_path: str
    """
    key = video_key.format(video_path=video_path)
    region.delete(key)
    logger.debug(u'Cached video information under key %s was invalidated', key)