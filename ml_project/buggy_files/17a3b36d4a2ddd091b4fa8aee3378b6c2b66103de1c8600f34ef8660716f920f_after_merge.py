def search_providers(show, episodes, forced_search=False, down_cur_quality=False,
                     manual_search=False, manual_search_type=u'episode'):
    """
    Walk providers for information on shows.

    :param show: Show we are looking for
    :param episodes: List, episodes we hope to find
    :param forced_search: Boolean, is this a forced search?
    :param down_cur_quality: Boolean, should we re-download currently available quality file
    :param manual_search: Boolean, should we choose what to download?
    :param manual_search_type: Episode or Season search
    :return: results for search
    """
    found_results = {}
    final_results = []
    manual_search_results = []

    did_search = False

    # build name cache for show
    name_cache.build_name_cache(show)

    original_thread_name = threading.currentThread().name

    if manual_search:
        log.info(u'Using manual search providers')
        providers = [x for x in sorted_provider_list(app.RANDOMIZE_PROVIDERS)
                     if x.is_active() and x.enable_manualsearch]
    else:
        log.info(u'Using backlog search providers')
        providers = [x for x in sorted_provider_list(app.RANDOMIZE_PROVIDERS)
                     if x.is_active() and x.enable_backlog]

    threading.currentThread().name = original_thread_name

    for cur_provider in providers:
        threading.currentThread().name = original_thread_name + u' :: [' + cur_provider.name + u']'

        if cur_provider.anime_only and not show.is_anime:
            log.debug(u'{0} is not an anime, skipping', show.name)
            continue

        found_results[cur_provider.name] = {}

        search_count = 0
        search_mode = cur_provider.search_mode

        # Always search for episode when manually searching when in sponly
        if search_mode == u'sponly' and (forced_search or manual_search):
            search_mode = u'eponly'

        if manual_search and manual_search_type == u'season':
            search_mode = u'sponly'

        while True:
            search_count += 1

            if search_mode == u'eponly':
                log.info(u'Performing episode search for {0}', show.name)
            else:
                log.info(u'Performing season pack search for {0}', show.name)

            try:
                search_results = cur_provider.find_search_results(show, episodes, search_mode, forced_search,
                                                                  down_cur_quality, manual_search, manual_search_type)
            except AuthException as error:
                log.error(u'Authentication error: {0}', ex(error))
                break
            except socket_timeout as error:
                log.debug(u'Connection timed out (sockets) while searching {0}. Error: {1!r}',
                          cur_provider.name, ex(error))
                break
            except (requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects) as error:
                log.debug(u'HTTP error while searching {0}. Error: {1!r}',
                          cur_provider.name, ex(error))
                break
            except requests.exceptions.ConnectionError as error:
                log.debug(u'Connection error while searching {0}. Error: {1!r}',
                          cur_provider.name, ex(error))
                break
            except requests.exceptions.Timeout as error:
                log.debug(u'Connection timed out while searching {0}. Error: {1!r}',
                          cur_provider.name, ex(error))
                break
            except requests.exceptions.ContentDecodingError as error:
                log.debug(u'Content-Encoding was gzip, but content was not compressed while searching {0}.'
                          u' Error: {1!r}', cur_provider.name, ex(error))
                break
            except Exception as error:
                if u'ECONNRESET' in error or (hasattr(error, u'errno') and error.errno == errno.ECONNRESET):
                    log.warning(u'Connection reseted by peer while searching {0}. Error: {1!r}',
                                cur_provider.name, ex(error))
                else:
                    log.debug(traceback.format_exc())
                    log.error(u'Unknown exception while searching {0}. Error: {1!r}',
                              cur_provider.name, ex(error))
                break

            did_search = True

            if search_results:
                # make a list of all the results for this provider
                for cur_ep in search_results:
                    if cur_ep in found_results[cur_provider.name]:
                        found_results[cur_provider.name][cur_ep] += search_results[cur_ep]
                    else:
                        found_results[cur_provider.name][cur_ep] = search_results[cur_ep]

                    # Sort the list by seeders if possible
                    if cur_provider.provider_type == u'torrent' or getattr(cur_provider, u'torznab', None):
                        found_results[cur_provider.name][cur_ep].sort(key=lambda d: int(d.seeders), reverse=True)

                break
            elif not cur_provider.search_fallback or search_count == 2:
                break

            # Don't fallback when doing manual season search
            if manual_search_type == u'season':
                break

            if search_mode == u'sponly':
                log.debug(u'Fallback episode search initiated')
                search_mode = u'eponly'
            else:
                log.debug(u'Fallback season pack search initiate')
                search_mode = u'sponly'

        # skip to next provider if we have no results to process
        if not found_results[cur_provider.name]:
            continue

        # Update the cache if a manual search is being run
        if manual_search:
            # Let's create a list with episodes that we where looking for
            if manual_search_type == u'season':
                # If season search type, we only want season packs
                searched_episode_list = [SEASON_RESULT]
            else:
                searched_episode_list = [episode_obj.episode for episode_obj in episodes] + [MULTI_EP_RESULT]
            for searched_episode in searched_episode_list:
                if (searched_episode in search_results and
                        cur_provider.cache.update_cache_manual_search(search_results[searched_episode])):
                    # If we have at least a result from one provider, it's good enough to be marked as result
                    manual_search_results.append(True)
            # Continue because we don't want to pick best results as we are running a manual search by user
            continue

        # pick the best season NZB
        best_season_result = None
        if SEASON_RESULT in found_results[cur_provider.name]:
            best_season_result = pick_best_result(found_results[cur_provider.name][SEASON_RESULT])

        highest_quality_overall = 0
        for cur_episode in found_results[cur_provider.name]:
            for cur_result in found_results[cur_provider.name][cur_episode]:
                if cur_result.quality != Quality.UNKNOWN and cur_result.quality > highest_quality_overall:
                    highest_quality_overall = cur_result.quality
        log.debug(u'The highest quality of any match is {0}', Quality.qualityStrings[highest_quality_overall])

        # see if every episode is wanted
        if best_season_result:
            searched_seasons = {str(x.season) for x in episodes}

            # get the quality of the season nzb
            season_quality = best_season_result.quality
            log.debug(u'The quality of the season {0} is {1}',
                      best_season_result.provider.provider_type,
                      Quality.qualityStrings[season_quality])
            main_db_con = db.DBConnection()
            selection = main_db_con.select(
                'SELECT episode '
                'FROM tv_episodes '
                'WHERE showid = ?'
                ' AND ( season IN ( {0} ) )'.format(','.join(searched_seasons)),
                [show.indexerid]
            )
            all_eps = [int(x[b'episode']) for x in selection]
            log.debug(u'Episode list: {0}', all_eps)

            all_wanted = True
            any_wanted = False
            for cur_ep_num in all_eps:
                for season in {x.season for x in episodes}:
                    if not show.want_episode(season, cur_ep_num, season_quality, down_cur_quality):
                        all_wanted = False
                    else:
                        any_wanted = True

            # if we need every ep in the season and there's nothing better then
            # just download this and be done with it (unless single episodes are preferred)
            if all_wanted and best_season_result.quality == highest_quality_overall:
                log.info(u'All episodes in this season are needed, downloading {0} {1}',
                         best_season_result.provider.provider_type,
                         best_season_result.name)
                ep_objs = []
                for cur_ep_num in all_eps:
                    for season in {x.season for x in episodes}:
                        ep_objs.append(show.get_episode(season, cur_ep_num))
                best_season_result.episodes = ep_objs

                # Remove provider from thread name before return results
                threading.currentThread().name = original_thread_name

                return [best_season_result]

            elif not any_wanted:
                log.debug(u'No episodes in this season are needed at this quality, ignoring {0} {1}',
                          best_season_result.provider.provider_type,
                          best_season_result.name)
            else:
                if best_season_result.provider.provider_type == GenericProvider.NZB:
                    log.debug(u'Breaking apart the NZB and adding the individual ones to our results')

                    # if not, break it apart and add them as the lowest priority results
                    individual_results = nzb_splitter.split_result(best_season_result)
                    for cur_result in individual_results:
                        if len(cur_result.episodes) == 1:
                            ep_number = cur_result.episodes[0].episode
                        elif len(cur_result.episodes) > 1:
                            ep_number = MULTI_EP_RESULT

                        if ep_number in found_results[cur_provider.name]:
                            found_results[cur_provider.name][ep_number].append(cur_result)
                        else:
                            found_results[cur_provider.name][ep_number] = [cur_result]

                # If this is a torrent all we can do is leech the entire torrent,
                # user will have to select which eps not do download in his torrent client
                else:
                    # Season result from Torrent Provider must be a full-season torrent,
                    # creating multi-ep result for it.
                    log.info(u'Adding multi-ep result for full-season torrent.'
                             u' Undesired episodes can be skipped in torrent client if desired!')
                    ep_objs = []
                    for cur_ep_num in all_eps:
                        for season in {x.season for x in episodes}:
                            ep_objs.append(show.get_episode(season, cur_ep_num))
                    best_season_result.episodes = ep_objs

                    if MULTI_EP_RESULT in found_results[cur_provider.name]:
                        found_results[cur_provider.name][MULTI_EP_RESULT].append(best_season_result)
                    else:
                        found_results[cur_provider.name][MULTI_EP_RESULT] = [best_season_result]

        # go through multi-ep results and see if we really want them or not, get rid of the rest
        multi_results = {}
        if MULTI_EP_RESULT in found_results[cur_provider.name]:
            for _multi_result in found_results[cur_provider.name][MULTI_EP_RESULT]:
                log.debug(u'Seeing if we want to bother with multi-episode result {0}', _multi_result.name)

                # Filter result by ignore/required/whitelist/blacklist/quality, etc
                multi_result = pick_best_result(_multi_result)
                if not multi_result:
                    continue

                # see how many of the eps that this result covers aren't covered by single results
                needed_eps = []
                not_needed_eps = []
                for ep_obj in multi_result.episodes:
                    # if we have results for the episode
                    if ep_obj.episode in found_results[cur_provider.name] and \
                            len(found_results[cur_provider.name][ep_obj.episode]) > 0:
                        not_needed_eps.append(ep_obj.episode)
                    else:
                        needed_eps.append(ep_obj.episode)

                log.debug(u'Single-ep check result is needed_eps: {0}, not_needed_eps: {1}',
                          needed_eps, not_needed_eps)

                if not needed_eps:
                    log.debug(u'All of these episodes were covered by single episode results,'
                              u' ignoring this multi-episode result')
                    continue

                # check if these eps are already covered by another multi-result
                multi_needed_eps = []
                multi_not_needed_eps = []
                for ep_obj in multi_result.episodes:
                    if ep_obj.episode in multi_results:
                        multi_not_needed_eps.append(ep_obj.episode)
                    else:
                        multi_needed_eps.append(ep_obj.episode)

                log.debug(u'Multi-ep check result is multi_needed_eps: {0}, multi_not_needed_eps: {1}',
                          multi_needed_eps,
                          multi_not_needed_eps)

                if not multi_needed_eps:
                    log.debug(
                        u'All of these episodes were covered by another multi-episode nzb, '
                        u'ignoring this multi-ep result'
                    )
                    continue

                # don't bother with the single result if we're going to get it with a multi result
                for ep_obj in multi_result.episodes:
                    multi_results[ep_obj.episode] = multi_result
                    if ep_obj.episode in found_results[cur_provider.name]:
                        log.debug(
                            u'A needed multi-episode result overlaps with a single-episode result for episode {0},'
                            u' removing the single-episode results from the list',
                            ep_obj.episode,
                        )
                        del found_results[cur_provider.name][ep_obj.episode]

        # of all the single ep results narrow it down to the best one for each episode
        final_results += set(multi_results.values())
        for cur_ep in found_results[cur_provider.name]:
            if cur_ep in (MULTI_EP_RESULT, SEASON_RESULT):
                continue

            if not found_results[cur_provider.name][cur_ep]:
                continue

            # if all results were rejected move on to the next episode
            best_result = pick_best_result(found_results[cur_provider.name][cur_ep])
            if not best_result:
                continue

            # add result if its not a duplicate and
            found = False
            for i, result in enumerate(final_results):
                for best_resultEp in best_result.episodes:
                    if best_resultEp in result.episodes:
                        if result.quality < best_result.quality:
                            final_results.pop(i)
                        else:
                            found = True
            if not found:
                final_results += [best_result]

    if not did_search:
        log.warning(u'No NZB/Torrent providers found or enabled in the application config for backlog searches.'
                    u' Please check your settings.')

    # Remove provider from thread name before return results
    threading.currentThread().name = original_thread_name

    if manual_search:
        # If results in manual search return True, else False
        return any(manual_search_results)
    else:
        return final_results