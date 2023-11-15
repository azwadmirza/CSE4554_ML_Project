    def want_episode(self, season, episode, quality, forced_search=False, download_current_quality=False):
        """Whether or not the episode with the specified quality is wanted.

        :param season:
        :type season: int
        :param episode:
        :type episode: int
        :param quality:
        :type quality: int
        :param forced_search:
        :type forced_search: bool
        :param download_current_quality:
        :type download_current_quality: bool
        :return:
        :rtype: bool
        """
        # if the quality isn't one we want under any circumstances then just say no
        allowed_qualities, preferred_qualities = self.current_qualities
        logger.debug(u'{id}: Allowed, Preferred = [ {allowed} ] [ {preferred} ] Found = [ {found} ]',
                     id=self.indexerid, allowed=self.__qualities_to_string(allowed_qualities),
                     preferred=self.__qualities_to_string(preferred_qualities),
                     found=self.__qualities_to_string([quality]))

        if not Quality.wanted_quality(quality, allowed_qualities, preferred_qualities):
            logger.debug(u"{id}: Ignoring found result for '{show}' {ep} with unwanted quality '{quality}'",
                         id=self.indexerid, show=self.name, ep=episode_num(season, episode),
                         quality=Quality.qualityStrings[quality])
            return False

        main_db_con = db.DBConnection()
        sql_results = main_db_con.select(
            b'SELECT '
            b'  status, '
            b'  manually_searched '
            b'FROM '
            b'  tv_episodes '
            b'WHERE '
            b'  showid = ? '
            b'  AND season = ? '
            b'  AND episode = ?', [self.indexerid, season, episode])

        if not sql_results or not len(sql_results):
            logger.debug(u'{id}: Unable to find a matching episode in database. '
                         u"Ignoring found result for '{show}' {ep} with quality '{quality}'",
                         id=self.indexerid, show=self.name, ep=episode_num(season, episode),
                         quality=Quality.qualityStrings[quality])
            return False

        ep_status = int(sql_results[0][b'status'])
        ep_status_text = statusStrings[ep_status].upper()
        manually_searched = sql_results[0][b'manually_searched']
        _, cur_quality = Quality.split_composite_status(ep_status)

        # if it's one of these then we want it as long as it's in our allowed initial qualities
        if ep_status == WANTED:
            logger.debug(u"{id}: '{show}' {ep} status is 'WANTED'. Accepting result with quality '{new_quality}'",
                         id=self.indexerid, status=ep_status_text, show=self.name, ep=episode_num(season, episode),
                         new_quality=Quality.qualityStrings[quality])
            return True

        should_replace, reason = Quality.should_replace(ep_status, cur_quality, quality, allowed_qualities,
                                                        preferred_qualities, download_current_quality,
                                                        forced_search, manually_searched)
        logger.debug(u"{id}: '{show}' {ep} status is: '{status}'. {action} result with quality '{new_quality}'. "
                     u"Reason: {reason}", id=self.indexerid, show=self.name, ep=episode_num(season, episode),
                     status=ep_status_text, action='Accepting' if should_replace else 'Ignoring',
                     new_quality=Quality.qualityStrings[quality], reason=reason)
        return should_replace