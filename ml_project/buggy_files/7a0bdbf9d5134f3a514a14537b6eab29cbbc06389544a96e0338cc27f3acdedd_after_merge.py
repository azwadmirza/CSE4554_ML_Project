    def get_all_episodes(self, season=None, has_location=False):
        """Retrieve all episodes for this show given the specified filter.

        :param season:
        :type season: list
        :param has_location:
        :type has_location: bool
        :return:
        :rtype: list of Episode
        """
        # subselection to detect multi-episodes early, share_location > 0
        # If a multi-episode release has been downloaded. For example my.show.S01E1E2.1080p.WEBDL.mkv, you'll find the same location
        # in the database for those episodes (S01E01 and S01E02). The query is to mark that the location for each episode is shared with another episode.
        sql_selection = (b'SELECT season, episode, (SELECT '
                         b'  COUNT (*) '
                         b'FROM '
                         b'  tv_episodes '
                         b'WHERE '
                         b'  indexer = tve.indexer AND showid = tve.showid '
                         b'  AND season = tve.season '
                         b"  AND location != '' "
                         b'  AND location = tve.location '
                         b'  AND episode != tve.episode) AS share_location '
                         b'FROM tv_episodes tve WHERE indexer = ? AND showid = ?'
                         )
        sql_args = [self.indexer, self.series_id]

        if season is not None:
            sql_selection += b' AND season IN (?)'
            sql_args.append(','.join(map(text_type, season)))

        if has_location:
            sql_selection += b" AND location != ''"

        # need ORDER episode ASC to rename multi-episodes in order S01E01-02
        sql_selection += b' ORDER BY season ASC, episode ASC'

        main_db_con = db.DBConnection()
        results = main_db_con.select(sql_selection, sql_args)

        ep_list = []
        for cur_result in results:
            cur_ep = self.get_episode(cur_result[b'season'], cur_result[b'episode'])
            if not cur_ep:
                continue

            cur_ep.related_episodes = []
            if cur_ep.location:
                # if there is a location, check if it's a multi-episode (share_location > 0)
                # and put them in related_episodes
                if cur_result[b'share_location'] > 0:
                    related_eps_result = main_db_con.select(
                        b'SELECT '
                        b'  season, episode '
                        b'FROM '
                        b'  tv_episodes '
                        b'WHERE '
                        b'  showid = ? '
                        b'  AND season = ? '
                        b'  AND location = ? '
                        b'  AND episode != ? '
                        b'ORDER BY episode ASC',
                        [self.series_id, cur_ep.season, cur_ep.location, cur_ep.episode])
                    for cur_related_ep in related_eps_result:
                        related_ep = self.get_episode(cur_related_ep[b'season'], cur_related_ep[b'episode'])
                        if related_ep and related_ep not in cur_ep.related_episodes:
                            cur_ep.related_episodes.append(related_ep)
            ep_list.append(cur_ep)

        return ep_list