    def saveToDB(self, forceSave=False):

        if not self.dirty and not forceSave:
            # logger.log(str(self.indexerid) + ": Not saving show to db - record is not dirty", logger.DEBUG)
            return

        logger.log(u"%i: Saving to database: %s" % (self.indexerid, self.name), logger.DEBUG)

        controlValueDict = {"indexer_id": self.indexerid}
        newValueDict = {"indexer": self.indexer,
                        "show_name": self.name,
                        "location": self._location,
                        "network": self.network,
                        "genre": self.genre,
                        "classification": self.classification,
                        "runtime": self.runtime,
                        "quality": self.quality,
                        "airs": self.airs,
                        "status": self.status,
                        "flatten_folders": self.flatten_folders,
                        "paused": self.paused,
                        "air_by_date": self.air_by_date,
                        "anime": self.anime,
                        "scene": self.scene,
                        "sports": self.sports,
                        "subtitles": self.subtitles,
                        "dvdorder": self.dvdorder,
                        "startyear": self.startyear,
                        "lang": self.lang,
                        "imdb_id": self.imdbid,
                        "last_update_indexer": self.last_update_indexer,
                        "rls_ignore_words": self.rls_ignore_words,
                        "rls_require_words": self.rls_require_words,
                        "default_ep_status": self.default_ep_status}

        main_db_con = db.DBConnection()
        main_db_con.upsert("tv_shows", newValueDict, controlValueDict)

        helpers.update_anime_support()

        if self.imdbid and self.imdb_info.get('year'):
            controlValueDict = {"indexer_id": self.indexerid}
            newValueDict = self.imdb_info

            main_db_con = db.DBConnection()
            main_db_con.upsert("imdb_info", newValueDict, controlValueDict)