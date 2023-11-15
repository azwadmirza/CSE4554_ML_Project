    def when(self, matches, context):
        """Evaluate the rule.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context: dict
        :return:
        """
        # only for shows that seems to be animes
        if context.get('show_type') == 'normal' or not matches.tagged('anime') or \
                not matches.tagged('weak-duplicate') or matches.tagged('newpct'):
            return

        fileparts = matches.markers.named('path')
        for filepart in marker_sorted(fileparts, matches):
            season = matches.range(filepart.start, filepart.end, index=0,
                                   predicate=lambda match: match.name == 'season' and match.raw.isdigit())
            if not season:
                continue

            episode = matches.next(season, index=0,
                                   predicate=lambda match: (match.name == 'episode' and
                                                            match.end <= filepart.end and
                                                            match.raw.isdigit()))

            # there should be season and episode and the episode should start right after the season and both raw values
            # should be digit
            if season and episode and season.end == episode.start:
                # then make them an absolute episode:
                absolute_episode = copy.copy(episode)
                absolute_episode.name = 'absolute_episode'
                # raw value contains the season and episode altogether
                absolute_episode.value = int(episode.parent.raw if episode.parent else episode.raw)

                # always keep episode (subliminal needs it)
                corrected_episode = copy.copy(absolute_episode)
                corrected_episode.name = 'episode'

                to_remove = [season, episode]
                to_append = [absolute_episode, corrected_episode]
                return to_remove, to_append