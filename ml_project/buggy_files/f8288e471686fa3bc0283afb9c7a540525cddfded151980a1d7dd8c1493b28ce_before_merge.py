    def run(self):

        super(QueueItemAdd, self).run()

        if self.showDir:
            try:
                assert isinstance(self.showDir, six.text_type)
            except AssertionError:
                logger.log(traceback.format_exc(), logger.WARNING)
                self._finish_early()
                return

        logger.log('Starting to add show {0}'.format('by ShowDir: {0}'.format(self.showDir) if self.showDir else 'by Indexer Id: {0}'.format(self.indexer_id)))
        # make sure the Indexer IDs are valid
        try:
            s = sickchill.indexer.series_by_id(indexerid=self.indexer_id, indexer=self.indexer, language=self.lang)

            # Let's try to create the show Dir if it's not provided. This way we force the show dir to build build using the
            # Indexers provided series name
            if self.root_dir and not self.showDir:
                if not s.title:
                    logger.log('Unable to get a show {0}, can\'t add the show'.format(self.showDir))
                    self._finish_early()
                    return

                self.showDir = ek(os.path.join, self.root_dir, sanitize_filename(s.title))

                dir_exists = makeDir(self.showDir)
                if not dir_exists:
                    logger.log('Unable to create the folder {0}, can\'t add the show'.format(self.showDir))
                    self._finish_early()
                    return

                chmodAsParent(self.showDir)

            # this usually only happens if they have an NFO in their show dir which gave us a Indexer ID that has no proper english version of the show
            if getattr(s, 'seriesName', None) is None:
                # noinspection PyPep8
                error_string = 'Show in {0} has no name on {1}, probably searched with the wrong language. Delete .nfo and add manually in the correct language.'.format(
                    self.showDir, sickchill.indexer.name(self.indexer))

                logger.log(error_string, logger.WARNING)
                ui.notifications.error('Unable to add show', error_string)

                self._finish_early()
                return

            # if the show has no episodes/seasons
            if not s:
                error_string = 'Show {0} is on {1} but contains no season/episode data.'.format(
                    s.seriesName, sickchill.indexer.name(self.indexer))

                logger.log(error_string)
                ui.notifications.error('Unable to add show', error_string)

                self._finish_early()
                return
        except Exception as error:
            error_string = 'Unable to look up the show in {0} on {1} using ID {2}, not using the NFO. Delete .nfo and try adding manually again.'.format(
                self.showDir, sickchill.indexer.name(self.indexer), self.indexer_id)

            logger.log('{0}: {1}'.format(error_string, error), logger.ERROR)
            ui.notifications.error(
                'Unable to add show', error_string)

            if sickbeard.USE_TRAKT:
                trakt_api = TraktAPI(sickbeard.SSL_VERIFY, sickbeard.TRAKT_TIMEOUT)

                title = self.showDir.split('/')[-1]
                data = {
                    'shows': [
                        {
                            'title': title,
                            'ids': {sickchill.indexer.slug(self.indexer): self.indexer_id}
                        }
                    ]
                }
                trakt_api.traktRequest('sync/watchlist/remove', data, method='POST')

            self._finish_early()
            return

        try:
            try:
                newShow = TVShow(self.indexer, self.indexer_id, self.lang)
            except MultipleShowObjectsException as error:
                # If we have the show in our list, but the location is wrong, lets fix it and refresh!
                existing_show = Show.find(sickbeard.showList, self.indexer_id)
                # noinspection PyProtectedMember
                if existing_show and not ek(os.path.isdir, existing_show._location):
                    newShow = existing_show
                else:
                    raise error

            newShow.loadFromIndexer()

            self.show = newShow

            # set up initial values
            self.show.location = self.showDir
            self.show.subtitles = self.subtitles if self.subtitles is not None else sickbeard.SUBTITLES_DEFAULT
            self.show.subtitles_sr_metadata = self.subtitles_sr_metadata
            self.show.quality = self.quality if self.quality else sickbeard.QUALITY_DEFAULT
            self.show.season_folders = self.season_folders if self.season_folders is not None else sickbeard.SEASON_FOLDERS_DEFAULT
            self.show.anime = self.anime if self.anime is not None else sickbeard.ANIME_DEFAULT
            self.show.scene = self.scene if self.scene is not None else sickbeard.SCENE_DEFAULT
            self.show.paused = self.paused if self.paused is not None else False

            # set up default new/missing episode status
            logger.log('Setting all episodes to the specified default status: {0}' .format(self.show.default_ep_status))
            self.show.default_ep_status = self.default_status

            if self.show.anime:
                self.show.release_groups = BlackAndWhiteList(self.show.indexerid)
                if self.blacklist:
                    self.show.release_groups.set_black_keywords(self.blacklist)
                if self.whitelist:
                    self.show.release_groups.set_white_keywords(self.whitelist)

            # # be smart-ish about this
            # if self.show.genre and 'talk show' in self.show.genre.lower():
            #     self.show.air_by_date = 1
            # if self.show.genre and 'documentary' in self.show.genre.lower():
            #     self.show.air_by_date = 0
            # if self.show.classification and 'sports' in self.show.classification.lower():
            #     self.show.sports = 1

        except Exception as error:
            error_string = 'Unable to add {0} due to an error with {1}'.format(
                self.show.name if self.show else 'show', sickchill.indexer.name(self.indexer))

            logger.log('{0}: {1}'.format(error_string, error), logger.ERROR)

            logger.log('Error trying to add show: {0}'.format(error), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

            ui.notifications.error('Unable to add show', error_string)

            self._finish_early()
            return

        except MultipleShowObjectsException:
            error_string = 'The show in {0} is already in your show list, skipping'.format(self.showDir)
            logger.log(error_string, logger.WARNING)
            ui.notifications.error('Show skipped', error_string)

            self._finish_early()
            return

        logger.log('Retrieving show info from IMDb', logger.DEBUG)
        try:
            self.show.loadIMDbInfo()
        except imdb_exceptions.IMDbError as error:
            logger.log(' Something wrong on IMDb api: {0}'.format(error), logger.WARNING)
        except Exception as error:
            logger.log('Error loading IMDb info: {0}'.format(error), logger.ERROR)

        try:
            self.show.saveToDB()
        except Exception as error:
            logger.log('Error saving the show to the database: {0}'.format(error), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)
            self._finish_early()
            raise

        # add it to the show list
        if not Show.find(sickbeard.showList, self.indexer_id):
            sickbeard.showList.append(self.show)

        try:
            self.show.loadEpisodesFromIndexer()
        except Exception as error:
            logger.log('Error with {0}, not creating episode list: {1}'.format(self.show.idxr.name, error), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # update internal name cache
        name_cache.buildNameCache(self.show)

        try:
            self.show.loadEpisodesFromDir()
        except Exception as error:
            logger.log('Error searching dir for episodes: {0}'.format(error), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

        # if they set default ep status to WANTED then run the backlog to search for episodes
        # FIXME: This needs to be a backlog queue item!!!
        if self.show.default_ep_status == WANTED:
            logger.log('Launching backlog for this show since its episodes are WANTED')
            sickbeard.backlogSearchScheduler.action.searchBacklog([self.show])

        self.show.writeMetadata()
        self.show.updateMetadata()
        self.show.populateCache()

        self.show.flushEpisodes()

        if sickbeard.USE_TRAKT:
            # if there are specific episodes that need to be added by trakt
            sickbeard.traktCheckerScheduler.action.manageNewShow(self.show)
            # add show to trakt.tv library
            if sickbeard.TRAKT_SYNC:
                sickbeard.traktCheckerScheduler.action.addShowToTraktLibrary(self.show)

            if sickbeard.TRAKT_SYNC_WATCHLIST:
                logger.log('update watchlist')
                notifiers.trakt_notifier.update_watchlist(show_obj=self.show)

        # Load XEM data to DB for show
        scene_numbering.xem_refresh(self.show.indexerid, self.show.indexer, force=True)

        # check if show has XEM mapping so we can determine if searches should go by scene numbering or indexer numbering.
        if not self.scene and scene_numbering.get_xem_numbering_for_show(self.show.indexerid, self.show.indexer):
            self.show.scene = 1

        # After initial add, set to default_status_after.
        self.show.default_ep_status = self.default_status_after

        super(QueueItemAdd, self).finish()
        self.finish()