    def run(self):

        ShowQueueItem.run(self)

        logger.log(u"Starting to add show {0}".format("by ShowDir: {0}".format(self.showDir) if self.showDir else "by Indexer Id: {0}".format(self.indexer_id)))
        # make sure the Indexer IDs are valid
        try:

            lINDEXER_API_PARMS = sickbeard.indexerApi(self.indexer).api_params.copy()
            if self.lang:
                lINDEXER_API_PARMS['language'] = self.lang

            logger.log(u"" + str(sickbeard.indexerApi(self.indexer).name) + ": " + repr(lINDEXER_API_PARMS))

            t = sickbeard.indexerApi(self.indexer).indexer(**lINDEXER_API_PARMS)
            s = t[self.indexer_id]

            # Let's try to create the show Dir if it's not provided. This way we force the show dir to build build using the
            # Indexers provided series name
            if not self.showDir and self.root_dir:
                show_name = get_showname_from_indexer(self.indexer, self.indexer_id, self.lang)
                if show_name:
                    self.showDir = ek(os.path.join, self.root_dir, sanitize_filename(show_name))
                    dir_exists = makeDir(self.showDir)
                    if not dir_exists:
                        logger.log(u"Unable to create the folder {0}, can't add the show".format(self.showDir))
                        return

                    chmodAsParent(self.showDir)
                else:
                    logger.log(u"Unable to get a show {0}, can't add the show".format(self.showDir))
                    return

            # this usually only happens if they have an NFO in their show dir which gave us a Indexer ID that has no proper english version of the show
            if getattr(s, 'seriesname', None) is None:
                logger.log(u"Show in {} has no name on {}, probably searched with the wrong language.".format
                           (self.showDir, sickbeard.indexerApi(self.indexer).name), logger.ERROR)

                ui.notifications.error("Unable to add show",
                                       "Show in " + self.showDir + " has no name on " + str(sickbeard.indexerApi(
                                           self.indexer).name) + ", probably the wrong language. Delete .nfo and add manually in the correct language.")
                self._finishEarly()
                return
            # if the show has no episodes/seasons
            if not s:
                logger.log(u"Show " + str(s['seriesname']) + " is on " + str(
                    sickbeard.indexerApi(self.indexer).name) + " but contains no season/episode data.")
                ui.notifications.error("Unable to add show",
                                       "Show " + str(s['seriesname']) + " is on " + str(sickbeard.indexerApi(
                                           self.indexer).name) + " but contains no season/episode data.")
                self._finishEarly()
                return
        except Exception as e:
            logger.log(u"%s Error while loading information from indexer %s. Error: %r" % (self.indexer_id, sickbeard.indexerApi(self.indexer).name, ex(e)), logger.ERROR)
            # logger.log(u"Show name with ID %s doesn't exist on %s anymore. If you are using trakt, it will be removed from your TRAKT watchlist. If you are adding manually, try removing the nfo and adding again" %
            #            (self.indexer_id, sickbeard.indexerApi(self.indexer).name), logger.WARNING)

            ui.notifications.error(
                "Unable to add show",
                "Unable to look up the show in %s on %s using ID %s, not using the NFO. Delete .nfo and try adding manually again." %
                (self.showDir, sickbeard.indexerApi(self.indexer).name, self.indexer_id)
            )

            if sickbeard.USE_TRAKT:

                trakt_id = sickbeard.indexerApi(self.indexer).config['trakt_id']
                trakt_api = TraktAPI(sickbeard.SSL_VERIFY, sickbeard.TRAKT_TIMEOUT)

                title = self.showDir.split("/")[-1]
                data = {
                    'shows': [
                        {
                            'title': title,
                            'ids': {}
                        }
                    ]
                }
                if trakt_id == 'tvdb_id':
                    data['shows'][0]['ids']['tvdb'] = self.indexer_id
                else:
                    data['shows'][0]['ids']['tvrage'] = self.indexer_id

                trakt_api.traktRequest("sync/watchlist/remove", data, method='POST')

            self._finishEarly()
            return

        try:
            newShow = TVShow(self.indexer, self.indexer_id, self.lang)
            newShow.loadFromIndexer()

            self.show = newShow

            # set up initial values
            self.show.location = self.showDir
            self.show.subtitles = self.subtitles if self.subtitles is not None else sickbeard.SUBTITLES_DEFAULT
            self.show.quality = self.quality if self.quality else sickbeard.QUALITY_DEFAULT
            self.show.flatten_folders = self.flatten_folders if self.flatten_folders is not None else sickbeard.FLATTEN_FOLDERS_DEFAULT
            self.show.anime = self.anime if self.anime is not None else sickbeard.ANIME_DEFAULT
            self.show.scene = self.scene if self.scene is not None else sickbeard.SCENE_DEFAULT
            self.show.paused = self.paused if self.paused is not None else False

            # set up default new/missing episode status
            logger.log(u"Setting all episodes to the specified default status: " + str(self.show.default_ep_status))
            self.show.default_ep_status = self.default_status

            if self.show.anime:
                self.show.release_groups = BlackAndWhiteList(self.show.indexerid)
                if self.blacklist:
                    self.show.release_groups.set_black_keywords(self.blacklist)
                if self.whitelist:
                    self.show.release_groups.set_white_keywords(self.whitelist)

            # # be smartish about this
            # if self.show.genre and "talk show" in self.show.genre.lower():
            #     self.show.air_by_date = 1
            # if self.show.genre and "documentary" in self.show.genre.lower():
            #     self.show.air_by_date = 0
            # if self.show.classification and "sports" in self.show.classification.lower():
            #     self.show.sports = 1

        except sickbeard.indexer_exception as e:
            logger.log(
                u"Unable to add show due to an error with " + sickbeard.indexerApi(self.indexer).name + ": " + ex(e),
                logger.ERROR)
            if self.show:
                ui.notifications.error(
                    "Unable to add " + str(self.show.name) + " due to an error with " + sickbeard.indexerApi(
                        self.indexer).name + "")
            else:
                ui.notifications.error(
                    "Unable to add show due to an error with " + sickbeard.indexerApi(self.indexer).name + "")
            self._finishEarly()
            return

        except MultipleShowObjectsException:
            logger.log(u"The show in " + self.showDir + " is already in your show list, skipping", logger.WARNING)
            ui.notifications.error('Show skipped', "The show in " + self.showDir + " is already in your show list")
            self._finishEarly()
            return

        except Exception as e:
            logger.log(u"Error trying to add show: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)
            self._finishEarly()
            raise

        logger.log(u"Retrieving show info from IMDb", logger.DEBUG)
        try:
            self.show.load_imdb_info()
        except imdb_exceptions.IMDbError as e:
            logger.log(u"Something wrong on IMDb api: " + ex(e), logger.WARNING)
        except Exception as e:
            logger.log(u"Error loading IMDb info: " + ex(e), logger.ERROR)

        try:
            self.show.saveToDB()
        except Exception as e:
            logger.log(u"Error saving the show to the database: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)
            self._finishEarly()
            raise

        # add it to the show list
        sickbeard.showList.append(self.show)

        try:
            self.show.loadEpisodesFromIndexer()
        except Exception as e:
            logger.log(
                u"Error with " + sickbeard.indexerApi(self.show.indexer).name + ", not creating episode list: " + ex(e),
                logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # update internal name cache
        name_cache.buildNameCache(self.show)

        try:
            self.show.loadEpisodesFromDir()
        except Exception as e:
            logger.log(u"Error searching dir for episodes: " + ex(e), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # if they set default ep status to WANTED then run the backlog to search for episodes
        # FIXME: This needs to be a backlog queue item!!!
        if self.show.default_ep_status == WANTED:
            logger.log(u"Launching backlog for this show since its episodes are WANTED")
            sickbeard.backlogSearchScheduler.action.searchBacklog([self.show])

        self.show.writeMetadata()
        self.show.updateMetadata()
        self.show.populateCache()

        self.show.flushEpisodes()

        if sickbeard.USE_TRAKT:
            # if there are specific episodes that need to be added by trakt
            sickbeard.traktCheckerScheduler.action.manage_new_show(self.show)

            # add show to trakt.tv library
            if sickbeard.TRAKT_SYNC:
                sickbeard.traktCheckerScheduler.action.add_show_trakt_library(self.show)

            if sickbeard.TRAKT_SYNC_WATCHLIST:
                logger.log(u"update watchlist")
                notifiers.trakt_notifier.update_watchlist(show_obj=self.show)

        # Load XEM data to DB for show
        sickbeard.scene_numbering.xem_refresh(self.show.indexerid, self.show.indexer, force=True)

        # check if show has XEM mapping so we can determin if searches should go by scene numbering or indexer numbering.
        if not self.scene and sickbeard.scene_numbering.get_xem_numbering_for_show(self.show.indexerid,
                                                                                   self.show.indexer):
            self.show.scene = 1

        # After initial add, set to default_status_after.
        self.show.default_ep_status = self.default_status_after

        self.finish()