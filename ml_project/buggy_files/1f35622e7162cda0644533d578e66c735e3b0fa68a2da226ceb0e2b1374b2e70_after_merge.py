def get_min_score():
    """Return the min score to be used by subliminal.

    Perfect match = hash - resolution (subtitle for 720p is the same as for 1080p) - video_codec - audio_codec
    Non-perfect match = series + year + season + episode

    :return: min score to be used to download subtitles
    :rtype: int
    """
    if sickbeard.SUBTITLES_PERFECT_MATCH:
        return episode_scores['hash'] - (episode_scores['resolution'] +
                                         episode_scores['video_codec'] +
                                         episode_scores['audio_codec'])

    return episode_scores['series'] + episode_scores['year'] + episode_scores['season'] + episode_scores['episode']