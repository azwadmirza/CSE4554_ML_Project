    def _parse_string(self, name):
        guess = guessit.guessit(name, dict(show_type=self.show_type))
        result = self.to_parse_result(name, guess)

        show = helpers.get_show(result.series_name, self.try_indexers) if not self.naming_pattern else None

        # confirm passed in show object indexer id matches result show object indexer id
        show = None if show and self.show and show.indexerid != self.show.indexerid else show
        result.show = show or self.show

        # if this is a naming pattern test or result doesn't have a show object then return best result
        if not result.show or self.naming_pattern:
            return result

        # get quality
        result.quality = common.Quality.nameQuality(name, result.show.is_anime)
        if result.quality == common.Quality.UNKNOWN:
            result.quality = common.Quality.from_guessit(guess)

        new_episode_numbers = []
        new_season_numbers = []
        new_absolute_numbers = []

        # if we have an air-by-date show and the result is air-by-date,
        # then get the real season/episode numbers
        if result.show.air_by_date and result.is_air_by_date:
            logger.debug('Show {name} is air by date', name=show.name)
            airdate = result.air_date.toordinal()
            main_db_con = db.DBConnection()
            sql_result = main_db_con.select(
                b'SELECT season, episode FROM tv_episodes WHERE showid = ? and indexer = ? and airdate = ?',
                [result.show.indexerid, result.show.indexer, airdate])

            season_number = None
            episode_numbers = []

            if sql_result:
                season_number = int(sql_result[0][0])
                episode_numbers = [int(sql_result[0][1])]
                logger.debug('Database info for show {name}: S{season} E{episodes}',
                             name=show.name, season=season_number, episodes=episode_numbers)

            if season_number is None or not episode_numbers:
                logger.debug('Show {name} has no season or episodes, using indexer...', name=show.name)
                indexer_api = sickbeard.indexerApi(result.show.indexer)
                try:
                    indexer_api_params = indexer_api.api_params.copy()

                    if result.show.lang:
                        indexer_api_params['language'] = result.show.lang

                    t = sickbeard.indexerApi(result.show.indexer).indexer(**indexer_api_params)
                    tv_episode = t[result.show.indexerid].airedOn(result.air_date)[0]

                    season_number = int(tv_episode['seasonnumber'])
                    episode_numbers = [int(tv_episode['episodenumber'])]
                    logger.debug('Indexer info for show {name}: S{season}E{episodes}',
                                 name=show.name, season=season_number, episodes=episode_numbers)
                except sickbeard.indexer_episodenotfound:
                    logger.warn('Unable to find episode with date {date} for show {name} skipping',
                                date=result.air_date, name=show.name)
                    episode_numbers = []
                except sickbeard.indexer_error as e:
                    logger.warn('Unable to contact {indexer_api.name}: {ex!r}', indexer_api=indexer_api, ex=e)
                    episode_numbers = []

            for episode_number in episode_numbers:
                s = season_number
                e = episode_number

                if result.show.is_scene:
                    (s, e) = scene_numbering.get_indexer_numbering(result.show.indexerid,
                                                                   result.show.indexer,
                                                                   season_number,
                                                                   episode_number)
                    logger.debug('Scene show {name}, using indexer numbering: S{season}E{episodes}',
                                 name=show.name, season=s, episodes=e)
                new_episode_numbers.append(e)
                new_season_numbers.append(s)

        elif result.show.is_anime and result.is_anime:
            logger.debug('Scene show {name} is anime', name=show.name)
            scene_season = scene_exceptions.get_scene_exception_by_name(result.series_name)[1]
            for absolute_episode in result.ab_episode_numbers:
                a = absolute_episode

                if result.show.is_scene:
                    a = scene_numbering.get_indexer_absolute_numbering(result.show.indexerid,
                                                                       result.show.indexer, absolute_episode,
                                                                       True, scene_season)

                (s, e) = helpers.get_all_episodes_from_absolute_number(result.show, [a])
                logger.debug('Scene show {name} using indexer for absolute {absolute}: S{season}E{episodes}',
                             name=show.name, absolute=a, season=s, episodes=e)

                new_absolute_numbers.append(a)
                new_episode_numbers.extend(e)
                new_season_numbers.append(s)

        elif result.season_number and result.episode_numbers:
            for episode_number in result.episode_numbers:
                s = result.season_number
                e = episode_number

                if result.show.is_scene:
                    (s, e) = scene_numbering.get_indexer_numbering(result.show.indexerid,
                                                                   result.show.indexer,
                                                                   result.season_number,
                                                                   episode_number)
                    logger.debug('Scene show {name} using indexer numbering: S{season}E{episodes}',
                                 name=show.name, season=s, episodes=e)

                if result.show.is_anime:
                    a = helpers.get_absolute_number_from_season_and_episode(result.show, s, e)
                    if a:
                        new_absolute_numbers.append(a)
                        logger.debug('Scene anime show {name} using indexer with absolute {absolute}: S{season}E{episodes}',
                                     name=show.name, absolute=a, season=s, episodes=e)

                new_episode_numbers.append(e)
                new_season_numbers.append(s)

        # need to do a quick sanity check heregex.  It's possible that we now have episodes
        # from more than one season (by tvdb numbering), and this is just too much
        # for sickbeard, so we'd need to flag it.
        new_season_numbers = list(set(new_season_numbers))  # remove duplicates
        if len(new_season_numbers) > 1:
            raise InvalidNameException('Scene numbering results episodes from seasons {seasons}, (i.e. more than one) '
                                       'and Medusa does not support this. Sorry.'.format(seasons=new_season_numbers))

        # I guess it's possible that we'd have duplicate episodes too, so lets
        # eliminate them
        new_episode_numbers = list(set(new_episode_numbers))
        new_episode_numbers.sort()

        # maybe even duplicate absolute numbers so why not do them as well
        new_absolute_numbers = list(set(new_absolute_numbers))
        new_absolute_numbers.sort()

        if new_absolute_numbers:
            result.ab_episode_numbers = new_absolute_numbers

        if new_season_numbers and new_episode_numbers:
            result.episode_numbers = new_episode_numbers
            result.season_number = new_season_numbers[0]

        if result.show.is_scene:
            logger.debug('Converted parsed result {original} into {result}', original=result.original_name,
                         result=str(result))

        # CPU sleep
        time.sleep(0.02)

        return result