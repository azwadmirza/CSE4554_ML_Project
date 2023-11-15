    def find_search_results(self, show, episodes, search_mode, forced_search=False, download_current_quality=False,
                            manual_search=False, manual_search_type='episode'):
        """Search episodes based on param."""
        self._check_auth()
        self.show = show

        results = {}
        items_list = []

        for episode in episodes:
            if not manual_search:
                cache_result = self.cache.search_cache(episode, forced_search=forced_search,
                                                       down_cur_quality=download_current_quality)
                if cache_result:
                    if episode.episode not in results:
                        results[episode.episode] = cache_result
                    else:
                        results[episode.episode].extend(cache_result)

                    continue

            search_strings = []
            if (len(episodes) > 1 or manual_search_type == 'season') and search_mode == 'sponly':
                search_strings = self._get_season_search_strings(episode)
            elif search_mode == 'eponly':
                search_strings = self._get_episode_search_strings(episode)

            for search_string in search_strings:
                # Find results from the provider
                items_list += self.search(search_string, ep_obj=episode)

            # In season search, we can't loop in episodes lists as we only need one episode to get the season string
            if search_mode == 'sponly':
                break

        if len(results) == len(episodes):
            return results

        if items_list:
            # categorize the items into lists by quality
            items = defaultdict(list)
            for item in items_list:
                items[self.get_quality(item, anime=show.is_anime)].append(item)

            # temporarily remove the list of items with unknown quality
            unknown_items = items.pop(Quality.UNKNOWN, [])

            # make a generator to sort the remaining items by descending quality
            items_list = (items[quality] for quality in sorted(items, reverse=True))

            # unpack all of the quality lists into a single sorted list
            items_list = list(chain(*items_list))

            # extend the list with the unknown qualities, now sorted at the bottom of the list
            items_list.extend(unknown_items)

        cl = []

        # Move through each item and parse it into a quality
        search_results = []
        for item in items_list:

            # Make sure we start with a TorrentSearchResult, NZBDataSearchResult or NZBSearchResult search result obj.
            search_result = self.get_result()
            search_results.append(search_result)
            search_result.item = item
            search_result.download_current_quality = download_current_quality
            search_result.forced_search = forced_search

            (search_result.name, search_result.url) = self._get_title_and_url(item)
            (search_result.seeders, search_result.leechers) = self._get_result_info(item)

            search_result.size = self._get_size(item)
            search_result.pubdate = self._get_pubdate(item)

            search_result.result_wanted = True

            try:
                search_result.parsed_result = NameParser(parse_method=('normal', 'anime')[show.is_anime]
                                                         ).parse(search_result.name)
            except (InvalidNameException, InvalidShowException) as error:
                log.debug(error.message)
                search_result.add_cache_entry = False
                search_result.result_wanted = False
                continue

            # I don't know why i'm doing this. Maybe remove it later on all together, now i've added the parsed_result
            # to the search_result.
            search_result.show = search_result.parsed_result.show
            search_result.quality = search_result.parsed_result.quality
            search_result.release_group = search_result.parsed_result.release_group
            search_result.version = search_result.parsed_result.version
            search_result.actual_season = search_result.parsed_result.season_number
            search_result.actual_episodes = search_result.parsed_result.episode_numbers

            if not manual_search:
                if not (search_result.show.air_by_date or search_result.show.sports):
                    if search_mode == 'sponly':
                        if search_result.parsed_result.episode_numbers:
                            log.debug(
                                'This is supposed to be a season pack search but the result {0} is not a valid '
                                'season pack, skipping it', search_result.name
                            )
                            search_result.result_wanted = False
                            continue
                        elif not [ep for ep in episodes if
                                  search_result.parsed_result.season_number == (ep.season, ep.scene_season)
                                  [ep.show.is_scene]]:
                            log.debug(
                                'This season result {0} is for a season we are not searching for, '
                                'skipping it', search_result.name
                            )
                            search_result.result_wanted = False
                            continue
                    else:
                        # I'm going to split these up for better readability
                        # Check if at least got a season parsed.
                        if search_result.parsed_result.season_number is None:
                            log.debug(
                                "The result {0} doesn't seem to have a valid season that we are currently trying to "
                                "snatch, skipping it", search_result.name
                            )
                            search_result.result_wanted = False
                            continue

                        # Check if we at least got some episode numbers parsed.
                        if not search_result.parsed_result.episode_numbers:
                            log.debug(
                                "The result {0} doesn't seem to match an episode that we are currently trying to "
                                "snatch, skipping it", search_result.name
                            )
                            search_result.result_wanted = False
                            continue

                        # Compare the episodes and season from the result with what was searched.
                        if not [searched_episode for searched_episode in episodes
                                if searched_episode.season == search_result.parsed_result.season_number and
                                (searched_episode.episode, searched_episode.scene_episode)
                                [searched_episode.series.is_scene] in
                                search_result.parsed_result.episode_numbers]:
                            log.debug(
                                "The result {0} doesn't seem to match an episode that we are currently trying to "
                                "snatch, skipping it", search_result.name
                            )
                            search_result.result_wanted = False
                            continue

                    # We've performed some checks to decided if we want to continue with this result.
                    # If we've hit this, that means this is not an air_by_date and not a sports show. And it seems to be
                    # a valid result. Let's store the parsed season and episode number and continue.
                    search_result.actual_season = search_result.parsed_result.season_number
                    search_result.actual_episodes = search_result.parsed_result.episode_numbers
                else:
                    # air_by_date or sportshow.
                    search_result.same_day_special = False

                    if not search_result.parsed_result.is_air_by_date:
                        log.debug(
                            "This is supposed to be a date search but the result {0} didn't parse as one, "
                            "skipping it", search_result.name
                        )
                        search_result.result_wanted = False
                        continue
                    else:
                        # Use a query against the tv_episodes table, to match the parsed air_date against.
                        air_date = search_result.parsed_result.air_date.toordinal()
                        db = DBConnection()
                        sql_results = db.select(
                            'SELECT season, episode FROM tv_episodes WHERE showid = ? AND airdate = ?',
                            [search_result.show.indexerid, air_date]
                        )

                        if len(sql_results) == 2:
                            if int(sql_results[0][b'season']) == 0 and int(sql_results[1][b'season']) != 0:
                                search_result.actual_season = int(sql_results[1][b'season'])
                                search_result.actual_episodes = [int(sql_results[1][b'episode'])]
                                search_result.same_day_special = True
                            elif int(sql_results[1][b'season']) == 0 and int(sql_results[0][b'season']) != 0:
                                search_result.actual_season = int(sql_results[0][b'season'])
                                search_result.actual_episodes = [int(sql_results[0][b'episode'])]
                                search_result.same_day_special = True
                        elif len(sql_results) != 1:
                            log.warning(
                                "Tried to look up the date for the episode {0} but the database didn't return proper "
                                "results, skipping it", search_result.name
                            )
                            search_result.result_wanted = False
                            continue

                        # @TODO: Need to verify and test this.
                        if search_result.result_wanted and not search_result.same_day_special:
                            search_result.actual_season = int(sql_results[0][b'season'])
                            search_result.actual_episodes = [int(sql_results[0][b'episode'])]

        # Iterate again over the search results, and see if there is anything we want.
        for search_result in search_results:

            # Try to cache the item if we want to.
            cache_result = search_result.add_result_to_cache(self.cache)
            if cache_result is not None:
                cl.append(cache_result)

            if not search_result.result_wanted:
                log.debug("We aren't interested in this result: {0} with url: {1}",
                          search_result.name, search_result.url)
                continue

            log.debug('Found result {0} at {1}', search_result.name, search_result.url)

            episode_object = search_result.create_episode_object()
            # result = self.get_result(episode_object, search_result)
            search_result.finish_search_result(self)

            if not episode_object:
                episode_number = SEASON_RESULT
                log.debug('Found season pack result {0} at {1}', search_result.name, search_result.url)
            elif len(episode_object) == 1:
                episode_number = episode_object[0].episode
                log.debug('Found single episode result {0} at {1}', search_result.name, search_result.url)
            else:
                episode_number = MULTI_EP_RESULT
                log.debug('Found multi-episode ({0}) result {1} at {2}',
                          ', '.join(search_result.parsed_result.episode_numbers),
                          search_result.name,
                          search_result.url)
            if episode_number not in results:
                results[episode_number] = [search_result]
            else:
                results[episode_number].append(search_result)

        if cl:
            # Access to a protected member of a client class
            db = self.cache._get_db()
            db.mass_action(cl)

        return results