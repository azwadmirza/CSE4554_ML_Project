def rules():
    """Return all custom rules to be applied to guessit default api.

    IMPORTANT! The order is important.
    Certain rules needs to be executed first, and others should be executed at the end.
    DO NOT define priority or dependency in each rule, it can become a mess. Better to just define the correct order
    in this method.

    Builder for rebulk object.
    :return: Created Rebulk object
    :rtype: Rebulk
    """
    return Rebulk().rules(
        FixTvChaosUkWorkaround,
        FixAnimeReleaseGroup,
        SpanishNewpctReleaseName,
        FixInvalidTitleOrAlternativeTitle,
        FixSeasonAndEpisodeConflicts,
        FixWrongTitleDueToFilmTitle,
        FixSeasonNotDetected,
        FixWrongSeasonRangeDetectionDueToEpisode,
        FixSeasonRangeDetection,
        FixEpisodeRangeDetection,
        FixEpisodeRangeWithSeasonDetection,
        FixWrongTitlesWithCompleteKeyword,
        AnimeWithSeasonAbsoluteEpisodeNumbers,
        AnimeAbsoluteEpisodeNumbers,
        AbsoluteEpisodeNumbers,
        PartsAsEpisodeNumbers,
        ExpectedTitlePostProcessor,
        CreateAliasWithAlternativeTitles,
        CreateAliasWithCountryOrYear,
        EnhanceReleaseGroupDetection,
        ReleaseGroupPostProcessor,
        FixMultipleTitles
    )