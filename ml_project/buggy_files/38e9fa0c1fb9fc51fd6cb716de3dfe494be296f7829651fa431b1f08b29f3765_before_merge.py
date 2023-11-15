    def _parse_anime(result):
        """
        Parse anime season episode results.

        Translate scene episode and season numbering to indexer numbering,
        using anime scen episode/season translation tables to indexer episode/season.

        :param result: Guessit parse result object.
        :return: tuple of found indexer episode numbers and indexer season numbers
        """
        log.debug('Scene numbering enabled series {name} is anime',
                  {'name': result.series.name})

        new_episode_numbers = []
        new_season_numbers = []
        new_absolute_numbers = []

        # Try to translate the scene series name to a scene number.
        # For example Jojo's bizarre Adventure - Diamond is unbreakable, will use xem, to translate the
        # "diamond is unbreakable" exception back to season 4 of it's "master" table. This will be used later
        # to translate it to an absolute number, which in turn can be translated to an indexer SxEx.
        # For example Diamond is unbreakable - 26 -> Season 4 -> Absolute number 100 -> tvdb S03E26
        scene_season = scene_exceptions.get_scene_exceptions_by_name(result.series_name)[0][1]

        if result.ab_episode_numbers:
            for absolute_episode in result.ab_episode_numbers:
                a = absolute_episode

                # Apparently we got a scene_season using the season scene exceptions. If we also do not have a season
                # parsed, guessit made a 'mistake' and it should have set the season with the value.
                # This is required for titles like: '[HorribleSubs].Kekkai.Sensen.&.Beyond.-.01.[1080p].mkv'
                #
                # Don't assume that scene_exceptions season is the same as indexer season.
                # E.g.: [HorribleSubs] Cardcaptor Sakura Clear Card - 08 [720p].mkv thetvdb s04, thexem s02
                if result.series.is_scene or (result.season_number is None and scene_season > 0):
                    a = scene_numbering.get_indexer_absolute_numbering(
                        result.series, absolute_episode, True, scene_season
                    )

                # Translate the absolute episode number, back to the indexers season and episode.
                (season, episode) = helpers.get_all_episodes_from_absolute_number(result.series, [a])

                if result.season_number is None and scene_season > 0:
                    log.debug(
                        'Detected a season scene exception [{series_name} -> {scene_season}] without a '
                        'season number in the title, '
                        'translating the episode absolute # [{scene_absolute}] to season #[{absolute_season}] and '
                        'episode #[{absolute_episode}].',
                        {'series_name': result.series_name, 'scene_season': scene_season, 'scene_absolute': a,
                         'absolute_season': season, 'absolute_episode': episode}
                    )
                else:
                    log.debug(
                        'Scene numbering enabled series {name} using indexer for absolute {absolute}: {ep}',
                        {'name': result.series.name, 'absolute': a, 'ep': episode_num(season, episode, 'absolute')}
                    )

                new_absolute_numbers.append(a)
                new_episode_numbers.extend(episode)
                new_season_numbers.append(season)

        # It's possible that we map a parsed result to an anime series,
        # but the result is not detected/parsed as an anime. In that case, we're using the result.episode_numbers.
        else:
            for episode_number in result.episode_numbers:
                season = result.season_number
                episode = episode_number
                a = helpers.get_absolute_number_from_season_and_episode(result.series, season, episode)
                if a:
                    new_absolute_numbers.append(a)
                    log.debug(
                        'Scene numbering enabled anime {name} using indexer with absolute {absolute}: {ep}',
                        {'name': result.series.name, 'absolute': a, 'ep': episode_num(season, episode, 'absolute')}
                    )

                new_episode_numbers.append(episode)
                new_season_numbers.append(season)

        return new_episode_numbers, new_season_numbers, new_absolute_numbers