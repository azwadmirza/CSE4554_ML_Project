def pick_best_result(results):  # pylint: disable=too-many-branches
    """
    Find the best result out of a list of search results for a show.

    :param results: list of result objects
    :return: best result object
    """
    results = results if isinstance(results, list) else [results]

    log.debug(u'Picking the best result out of {0}', [x.name for x in results])

    best_result = None

    # find the best result for the current episode
    for cur_result in results:
        assert cur_result.show, 'Every SearchResult object should have a show object available at this point.'

        # Every SearchResult object should have a show attribute available at this point.
        show = cur_result.show

        # build the black and white list
        if show.is_anime:
            if not show.release_groups.is_valid(cur_result):
                continue

        log.info(u'Quality of {0} is {1}', cur_result.name, Quality.qualityStrings[cur_result.quality])

        allowed_qualities, preferred_qualities = show.current_qualities

        if cur_result.quality not in allowed_qualities + preferred_qualities:
            log.debug(u'{0} is an unwanted quality, rejecting it', cur_result.name)
            continue

        wanted_ep = True

        if cur_result.actual_episodes:
            wanted_ep = False
            for episode in cur_result.actual_episodes:
                if show.want_episode(cur_result.actual_season, episode, cur_result.quality, cur_result.forced_search,
                                     cur_result.download_current_quality, search_type=cur_result.search_type):
                    wanted_ep = True

        if not wanted_ep:
            continue

        # If doesnt have min seeders OR min leechers then discard it
        if cur_result.seeders not in (-1, None) and cur_result.leechers not in (-1, None) \
            and hasattr(cur_result.provider, u'minseed') and hasattr(cur_result.provider, u'minleech') \
            and (int(cur_result.seeders) < int(cur_result.provider.minseed) or
                 int(cur_result.leechers) < int(cur_result.provider.minleech)):
            log.info(
                u'Discarding torrent because it does not meet the minimum provider setting '
                u'S:{0} L:{1}. Result has S:{2} L:{3}',
                cur_result.provider.minseed,
                cur_result.provider.minleech,
                cur_result.seeders,
                cur_result.leechers,
            )
            continue

        ignored_words = show.show_words().ignored_words
        required_words = show.show_words().required_words
        found_ignored_word = naming.contains_at_least_one_word(cur_result.name, ignored_words)
        found_required_word = naming.contains_at_least_one_word(cur_result.name, required_words)

        if ignored_words and found_ignored_word:
            log.info(u'Ignoring {0} based on ignored words filter: {1}', cur_result.name, found_ignored_word)
            continue

        if required_words and not found_required_word:
            log.info(u'Ignoring {0} based on required words filter: {1}', cur_result.name, required_words)
            continue

        if not naming.filter_bad_releases(cur_result.name, parse=False):
            continue

        if hasattr(cur_result, u'size'):
            if app.USE_FAILED_DOWNLOADS and failed_history.has_failed(cur_result.name, cur_result.size,
                                                                      cur_result.provider.name):
                log.info(u'{0} has previously failed, rejecting it', cur_result.name)
                continue

        preferred_words = ''
        if app.PREFERRED_WORDS:
            preferred_words = app.PREFERRED_WORDS.lower().split(u',')
        undesired_words = ''
        if app.UNDESIRED_WORDS:
            undesired_words = app.UNDESIRED_WORDS.lower().split(u',')

        if not best_result:
            best_result = cur_result
        if Quality.is_higher_quality(best_result.quality, cur_result.quality, allowed_qualities, preferred_qualities):
            best_result = cur_result
        elif best_result.quality == cur_result.quality:
            if any(ext in cur_result.name.lower() for ext in preferred_words):
                log.info(u'Preferring {0} (preferred words)', cur_result.name)
                best_result = cur_result
            if cur_result.proper_tags:
                log.info(u'Preferring {0} (repack/proper/real/rerip over nuked)', cur_result.name)
                best_result = cur_result
            if any(ext in best_result.name.lower() for ext in undesired_words) and not any(ext in cur_result.name.lower() for ext in undesired_words):
                log.info(u'Unwanted release {0} (contains undesired word(s))', cur_result.name)
                best_result = cur_result

    if best_result:
        log.debug(u'Picked {0} as the best', best_result.name)
    else:
        log.debug(u'No result picked.')

    return best_result