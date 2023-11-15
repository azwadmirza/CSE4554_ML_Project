    def _parse_string(self, name, skip_scene_detection=False):
        if not name:
            return

        matches = []
        best_result = None

        for (cur_regex_num, cur_regex_name, cur_regex) in self.compiled_regexes:
            match = cur_regex.match(name)

            if not match:
                continue

            result = ParseResult(name)
            result.which_regex = [cur_regex_name]
            result.score = 0 - cur_regex_num

            named_groups = list(match.groupdict())

            if 'series_name' in named_groups:
                result.series_name = match.group('series_name')
                if result.series_name:
                    result.series_name = self.clean_series_name(result.series_name)
                    result.score += 1

            if 'series_num' in named_groups and match.group('series_num'):
                result.score += 1

            if 'season_num' in named_groups:
                tmp_season = int(match.group('season_num'))
                if cur_regex_name == 'bare' and tmp_season in (19, 20):
                    continue
                if cur_regex_name == 'fov' and tmp_season > 500:
                    continue

                result.season_number = tmp_season
                result.score += 1

            if 'ep_num' in named_groups:
                ep_num = self._convert_number(match.group('ep_num'))
                if 'extra_ep_num' in named_groups and match.group('extra_ep_num'):
                    tmp_episodes = list(range(ep_num, self._convert_number(match.group('extra_ep_num')) + 1))
                    if len(tmp_episodes) > 4:
                        continue
                else:
                    tmp_episodes = [ep_num]

                result.episode_numbers = tmp_episodes
                result.score += 3

            if 'ep_ab_num' in named_groups:
                ep_ab_num = self._convert_number(match.group('ep_ab_num'))
                if 'extra_ab_ep_num' in named_groups and match.group('extra_ab_ep_num'):
                    result.ab_episode_numbers = list(range(ep_ab_num,
                                                           self._convert_number(match.group('extra_ab_ep_num')) + 1))
                    result.score += 1
                else:
                    result.ab_episode_numbers = [ep_ab_num]
                result.score += 1

            if 'air_date' in named_groups:
                air_date = match.group('air_date')
                try:
                    # Workaround for shows that get interpreted as 'air_date' incorrectly.
                    # Shows so far are 11.22.63 and 9-1-1
                    excluded_shows = ['112263', '911']
                    assert re.sub(r'[^\d]*', '', air_date) not in excluded_shows

                    # noinspection PyUnresolvedReferences
                    check = dateutil.parser.parse(air_date, fuzzy_with_tokens=True)[0].date()
                    # Make sure a 20th century date isn't returned as a 21st century date
                    # 1 Year into the future (No releases should be coming out a year ahead of time, that's just insane)
                    if check > check.today() and (check - check.today()).days // 365 > 1:
                        check = check.replace(year=check.year - 100)

                    result.air_date = check
                    result.score += 1
                except Exception as error:
                    logger.debug(error)
                    continue

            if 'extra_info' in named_groups:
                tmp_extra_info = match.group('extra_info')

                # Show.S04.Special or Show.S05.Part.2.Extras is almost certainly not every episode in the season
                if tmp_extra_info and cur_regex_name == 'season_only' and re.search(
                        r'([. _-]|^)(special|extra)s?\w*([. _-]|$)', tmp_extra_info, re.I):
                    continue
                result.extra_info = tmp_extra_info
                result.score += 1

            if 'release_group' in named_groups:
                result.release_group = match.group('release_group')
                result.score += 1

            if 'version' in named_groups:
                # assigns version to anime file if detected using anime regex. Non-anime regex receives -1
                version = match.group('version')
                if version:
                    result.version = version
                else:
                    result.version = 1
            else:
                result.version = -1

            matches.append(result)

        # only get matches with series_name
        # TODO: This makes tests fail when checking filenames that do not include the show name (refresh, force update, etc)
        # matches = [x for x in matches if x.series_name]

        if matches:
            # pick best match with highest score based on placement
            best_result = max(sorted(matches, reverse=True, key=attrgetter('which_regex')), key=attrgetter('score'))

            show = None
            if best_result and best_result.series_name and not self.naming_pattern:
                # try and create a show object for this result
                show = helpers.get_show(best_result.series_name, self.tryIndexers)

            # confirm passed in show object indexer id matches result show object indexer id
            if show:
                if self.showObj and show.indexerid != self.showObj.indexerid:
                    show = None

                # if show is an anime, try to use an anime expression first
                if show.is_anime:
                    anime_matches = [x for x in matches if x.is_anime]
                    if anime_matches:
                        best_result_anime = max(sorted(anime_matches, reverse=True, key=attrgetter('which_regex')), key=attrgetter('score'))
                        if best_result_anime and best_result_anime.series_name:
                            show_anime = helpers.get_show(best_result_anime.series_name)
                            if show_anime and show_anime.indexerid == show.indexerid:
                                best_result = best_result_anime

                best_result.show = show
            elif not show and self.showObj:
                best_result.show = self.showObj

            # if this is a naming pattern test or result doesn't have a show object then return best result
            if not best_result.show or self.naming_pattern:
                return best_result

            # get quality
            best_result.quality = common.Quality.nameQuality(name, best_result.show.is_anime)

            new_episode_numbers = []
            new_season_numbers = []
            new_absolute_numbers = []

            # if we have an air-by-date show then get the real season/episode numbers
            if best_result.is_air_by_date:
                airdate = best_result.air_date.toordinal()
                main_db_con = db.DBConnection()
                sql_result = main_db_con.select(
                    "SELECT season, episode FROM tv_episodes WHERE showid = ? and indexer = ? and airdate = ?",
                    [best_result.show.indexerid, best_result.show.indexer, airdate])

                season_number = None
                episode_numbers = []

                if sql_result:
                    season_number = int(sql_result[0][0])
                    episode_numbers = [int(sql_result[0][1])]

                if season_number is None or not episode_numbers:
                    try:
                        epObj = sickchill.indexer.episode(best_result.show, firstAired=best_result.air_date)
                        season_number = epObj["airedSeason"]
                        episode_numbers = [epObj["airedEpisode"]]
                    except Exception:
                        logger.warning(f"Unable to find episode with date {best_result.air_date} for show {best_result.show.name}, skipping")
                        episode_numbers = []

                for epNo in episode_numbers:
                    s = season_number
                    e = epNo

                    if best_result.show.is_scene:
                        (s, e) = scene_numbering.get_indexer_numbering(best_result.show.indexerid,
                                                                       best_result.show.indexer,
                                                                       season_number,
                                                                       epNo)
                    new_episode_numbers.append(e)
                    new_season_numbers.append(s)

            elif best_result.show.is_anime and best_result.ab_episode_numbers:
                best_result.scene_season = scene_exceptions.get_scene_exception_by_name(best_result.series_name)[1]
                for epAbsNo in best_result.ab_episode_numbers:
                    a = epAbsNo

                    if best_result.show.is_scene and not skip_scene_detection:
                        a = scene_numbering.get_indexer_absolute_numbering(best_result.show.indexerid,
                                                                           best_result.show.indexer, epAbsNo,
                                                                           True, best_result.scene_season)

                    (s, e) = helpers.get_all_episodes_from_absolute_number(best_result.show, [a])

                    new_absolute_numbers.append(a)
                    new_episode_numbers.extend(e)
                    new_season_numbers.append(s)

            elif best_result.season_number and best_result.episode_numbers:
                for epNo in best_result.episode_numbers:
                    s = best_result.season_number
                    e = epNo

                    if best_result.show.is_scene and not skip_scene_detection:
                        (s, e) = scene_numbering.get_indexer_numbering(best_result.show.indexerid,
                                                                       best_result.show.indexer,
                                                                       best_result.season_number,
                                                                       epNo)
                    if best_result.show.is_anime:
                        a = helpers.get_absolute_number_from_season_and_episode(best_result.show, s, e)
                        if a:
                            new_absolute_numbers.append(a)

                    new_episode_numbers.append(e)
                    new_season_numbers.append(s)

            # need to do a quick sanity check heregex.  It's possible that we now have episodes
            # from more than one season (by tvdb numbering), and this is just too much
            # for oldbeard, so we'd need to flag it.
            new_season_numbers = list(set(new_season_numbers))  # remove duplicates
            if len(new_season_numbers) > 1:
                raise InvalidNameException(f"Scene numbering results episodes from seasons {new_season_numbers}, "
                                           f"(i.e. more than one) and sickchill does not support this. Sorry.")

            # I guess it's possible that we'd have duplicate episodes too, so lets
            # eliminate them
            new_episode_numbers = sorted(set(new_episode_numbers))

            # maybe even duplicate absolute numbers so why not do them as well
            new_absolute_numbers = list(set(new_absolute_numbers))
            new_absolute_numbers.sort()

            if new_absolute_numbers:
                best_result.ab_episode_numbers = new_absolute_numbers

            if new_season_numbers and new_episode_numbers:
                best_result.episode_numbers = new_episode_numbers
                best_result.season_number = new_season_numbers[0]

            if best_result.show.is_scene and not skip_scene_detection:
                logger.debug(f"Converted parsed result {best_result.original_name} into {best_result}")

        # CPU sleep
        time.sleep(0.02)

        return best_result