def collectEpisodesFromSearchThread(show):
    """
    Collects all episodes from from the searchQueueScheduler and looks for episodes that are in status queued or searching.
    If episodes are found in FORCED_SEARCH_HISTORY, these are set to status finished.
    """
    episodes = []

    # Queued Searches
    searchstatus = SEARCH_STATUS_QUEUED
    for search_thread in sickbeard.searchQueueScheduler.action.get_all_ep_from_queue(show):
        episodes += getEpisodes(search_thread, searchstatus)

    # Running Searches
    searchstatus = SEARCH_STATUS_SEARCHING
    if sickbeard.searchQueueScheduler.action.is_manualsearch_in_progress():
        search_thread = sickbeard.searchQueueScheduler.action.currentItem

        if search_thread.success:
            searchstatus = SEARCH_STATUS_FINISHED

        episodes += getEpisodes(search_thread, searchstatus)

    # Finished Searches
    searchstatus = SEARCH_STATUS_FINISHED
    for search_thread in sickbeard.search_queue.FORCED_SEARCH_HISTORY:
        if show and not str(search_thread.show.indexerid) == show:
            continue

        if isinstance(search_thread, sickbeard.search_queue.ForcedSearchQueueItem) and \
            not [x for x in episodes if x['episodeindexid'] == search_thread.segment.indexerid]:
            episodes += getEpisodes(search_thread, searchstatus)
        else:
            # These are only Failed Downloads/Retry search thread items.. lets loop through the segment/episodes
            if not [i for i, j in zip(search_thread.segment, episodes) if i.indexerid == j['episodeindexid']]:
                episodes += getEpisodes(search_thread, searchstatus)

    return episodes