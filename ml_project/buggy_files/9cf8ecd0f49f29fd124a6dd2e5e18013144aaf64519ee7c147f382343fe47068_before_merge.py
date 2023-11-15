    def loadEpisodesFromDB(self):  # pylint: disable=too-many-locals

        logger.log(u"Loading all episodes from the DB", logger.DEBUG)
        scannedEps = {}

        try:
            main_db_con = db.DBConnection()
            sql = "SELECT season, episode, showid, show_name FROM tv_episodes JOIN tv_shows WHERE showid = indexer_id and showid = ?"
            sql_results = main_db_con.select(sql, [self.indexerid])
        except Exception as error:
            logger.log(u"Could not load episodes from the DB. Error: %s" % error, logger.ERROR)
            return scannedEps

        lINDEXER_API_PARMS = sickbeard.indexerApi(self.indexer).api_params.copy()

        if self.lang:
            lINDEXER_API_PARMS['language'] = self.lang
            logger.log(u"Using language: " + str(self.lang), logger.DEBUG)

        if self.dvdorder != 0:
            lINDEXER_API_PARMS['dvdorder'] = True

        # logger.log(u"lINDEXER_API_PARMS: " + str(lINDEXER_API_PARMS), logger.DEBUG)
        # Spamming log
        t = sickbeard.indexerApi(self.indexer).indexer(**lINDEXER_API_PARMS)

        cachedShow = t[self.indexerid]
        cachedSeasons = {}

        for curResult in sql_results:

            curSeason = int(curResult["season"])
            curEpisode = int(curResult["episode"])
            curShowid = int(curResult['showid'])
            curShowName = str(curResult['show_name'])

            logger.log(u"%s: Loading %s episodes from DB" % (curShowid, curShowName), logger.DEBUG)
            deleteEp = False

            if curSeason not in cachedSeasons:
                try:
                    cachedSeasons[curSeason] = cachedShow[curSeason]
                except sickbeard.indexer_seasonnotfound as error:
                    logger.log(u"%s: %s (unaired/deleted) in the indexer %s for %s. Removing existing records from database" %
                               (curShowid, error.message, sickbeard.indexerApi(self.indexer).name, curShowName), logger.DEBUG)
                    deleteEp = True

            if curSeason not in scannedEps:
                logger.log(u"{id}: Not curSeason in scannedEps".format(id=curShowid), logger.DEBUG)
                scannedEps[curSeason] = {}

            logger.log(u"{id}: Loading {show} {ep} from the DB".format
                       (id=curShowid, show=curShowName, ep=episode_num(curSeason, curEpisode)),
                       logger.DEBUG)

            try:
                curEp = self.getEpisode(curSeason, curEpisode)
                if not curEp:
                    raise EpisodeNotFoundException

                # if we found out that the ep is no longer on TVDB then delete it from our database too
                if deleteEp:
                    curEp.deleteEpisode()

                curEp.loadFromDB(curSeason, curEpisode)
                curEp.loadFromIndexer(tvapi=t, cachedSeason=cachedSeasons[curSeason])
                scannedEps[curSeason][curEpisode] = True
            except EpisodeDeletedException:
                logger.log(u"{id}: Tried loading {show} {ep} from the DB that should have been deleted, skipping it".format
                           (id=curShowid, show=curShowName, ep=episode_num(curSeason, curEpisode)),
                           logger.DEBUG)
                continue

        logger.log(u"{id}: Finished loading all episodes for {show} from the DB".format
                   (show=curShowName, id=curShowid), logger.DEBUG)

        return scannedEps