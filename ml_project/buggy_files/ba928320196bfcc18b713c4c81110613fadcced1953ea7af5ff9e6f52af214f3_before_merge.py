    def run(self):

        ShowQueueItem.run(self)

        logger.log(u"Beginning update of " + self.show.name, logger.DEBUG)

        logger.log(u"Retrieving show info from " + sickbeard.indexerApi(self.show.indexer).name + "", logger.DEBUG)
        try:
            self.show.loadFromIndexer(cache=not self.force)
        except sickbeard.indexer_error as e:
            logger.log(u"Unable to contact " + sickbeard.indexerApi(self.show.indexer).name + ", aborting: " + ex(e),
                       logger.WARNING)
            return
        except sickbeard.indexer_attributenotfound as e:
            logger.log(u"Data retrieved from " + sickbeard.indexerApi(
                self.show.indexer).name + " was incomplete, aborting: " + ex(e), logger.ERROR)
            return

        logger.log(u"Retrieving show info from IMDb", logger.DEBUG)
        try:
            self.show.loadIMDbInfo()
        except imdb_exceptions.IMDbError as e:
            logger.log(u" Something wrong on IMDb api: " + ex(e), logger.WARNING)
        except Exception as e:
            logger.log(u"Error loading IMDb info: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # have to save show before reading episodes from db
        try:
            self.show.saveToDB()
        except Exception as e:
            logger.log(u"Error saving show info to the database: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # get episode list from DB
        logger.log(u"Loading all episodes from the database", logger.DEBUG)
        DBEpList = self.show.loadEpisodesFromDB()

        # get episode list from TVDB
        logger.log(u"Loading all episodes from " + sickbeard.indexerApi(self.show.indexer).name + "", logger.DEBUG)
        try:
            IndexerEpList = self.show.loadEpisodesFromIndexer(cache=not self.force)
        except sickbeard.indexer_exception as e:
            logger.log(u"Unable to get info from " + sickbeard.indexerApi(
                self.show.indexer).name + ", the show info will not be refreshed: " + ex(e), logger.ERROR)
            IndexerEpList = None

        if IndexerEpList is None:
            logger.log(u"No data returned from " + sickbeard.indexerApi(
                self.show.indexer).name + ", unable to update this show", logger.ERROR)
        else:
            # for each ep we found on the Indexer delete it from the DB list
            for curSeason in IndexerEpList:
                for curEpisode in IndexerEpList[curSeason]:
                    curEp = self.show.getEpisode(curSeason, curEpisode)
                    curEp.saveToDB()

                    if curSeason in DBEpList and curEpisode in DBEpList[curSeason]:
                        del DBEpList[curSeason][curEpisode]

            # remaining episodes in the DB list are not on the indexer, just delete them from the DB
            for curSeason in DBEpList:
                for curEpisode in DBEpList[curSeason]:
                    logger.log(u"Permanently deleting episode " + str(curSeason) + "x" + str(
                        curEpisode) + " from the database", logger.INFO)
                    curEp = self.show.getEpisode(curSeason, curEpisode)
                    try:
                        curEp.deleteEpisode()
                    except EpisodeDeletedException:
                        pass

        # save show again, in case episodes have changed
        try:
            self.show.saveToDB()
        except Exception as e:
            logger.log(u"Error saving show info to the database: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        logger.log(u"Finished update of " + self.show.name, logger.DEBUG)

        sickbeard.showQueueScheduler.action.refreshShow(self.show, self.force)
        self.finish()