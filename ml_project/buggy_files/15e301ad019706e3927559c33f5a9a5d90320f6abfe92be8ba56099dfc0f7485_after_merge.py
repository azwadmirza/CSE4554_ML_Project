    def process(self):
        """
        Post-process a given file.

        :return: True on success, False on failure
        """
        self._log(u'Processing {0}'.format(self.file_path))

        if os.path.isdir(self.file_path):
            self._log(u'File {0} seems to be a directory'.format(self.file_path))
            return False

        if not os.path.exists(self.file_path):
            raise EpisodePostProcessingFailedException(u"File {0} doesn't exist, did unrar fail?".format
                                                       (self.file_path))

        for ignore_file in self.IGNORED_FILESTRINGS:
            if ignore_file in self.file_path:
                self._log(u'File {0} is ignored type, skipping'.format(self.file_path))
                return False

        # reset in_history
        self.in_history = False

        # reset the anidb episode object
        self.anidbEpisode = None

        # try to find the file info
        (show, season, episodes, quality, version) = self._find_info()
        if not show:
            raise EpisodePostProcessingFailedException(u"This show isn't in your list, you need to add it "
                                                       u"before post-processing an episode")
        elif season is None or not episodes:
            raise EpisodePostProcessingFailedException(u'Not enough information to determine what episode this is')

        # retrieve/create the corresponding Episode objects
        ep_obj = self._get_ep_obj(show, season, episodes)
        _, old_ep_quality = common.Quality.split_composite_status(ep_obj.status)

        # get the quality of the episode we're processing
        if quality and common.Quality.qualityStrings[quality] != 'Unknown':
            self._log(u'The episode file has a quality in it, using that: {0}'.format
                      (common.Quality.qualityStrings[quality]), logger.DEBUG)
            new_ep_quality = quality
        else:
            new_ep_quality = self._get_quality(ep_obj)

        logger.log(u'Quality of the episode we are processing: {0}'.format
                   (common.Quality.qualityStrings[new_ep_quality]), logger.DEBUG)

        # check snatched history to see if we should set the download as priority
        self._priority_from_history(show.indexerid, season, episodes, new_ep_quality)
        if self.in_history:
            self._log(u'This episode was found in history as SNATCHED.', logger.DEBUG)

        # see if this is a priority download (is it snatched, in history, PROPER, or BEST)
        priority_download = self._is_priority(old_ep_quality, new_ep_quality)
        self._log(u'This episode is a priority download: {0}'.format(priority_download), logger.DEBUG)

        # get the version of the episode we're processing (default is -1)
        if version != -1:
            self._log(u'Episode has a version in it, using that: v{0}'.format(version), logger.DEBUG)
        new_ep_version = version

        # check for an existing file
        existing_file_status = self._check_for_existing_file(ep_obj.location)

        if not priority_download:
            if existing_file_status == PostProcessor.EXISTS_SAME:
                self._log(u'File exists and the new file has the same size, aborting post-processing')
                return True

            if existing_file_status != PostProcessor.DOESNT_EXIST:
                if self.is_proper and new_ep_quality == old_ep_quality:
                    self._log(u'New file is a PROPER, marking it safe to replace')
                    self.flag_kodi_clean_library()
                else:
                    allowed_qualities, preferred_qualities = show.current_qualities
                    self._log(u'Checking if new quality {0} should replace current quality: {1}'.format
                              (common.Quality.qualityStrings[new_ep_quality],
                               common.Quality.qualityStrings[old_ep_quality]))
                    should_process, should_process_reason = self._should_process(old_ep_quality, new_ep_quality,
                                                                                 allowed_qualities, preferred_qualities)
                    if not should_process:
                        raise EpisodePostProcessingFailedException(
                            u'File exists. Marking it unsafe to replace. Reason: {0}'.format(should_process_reason))
                    else:
                        self._log(u'File exists. Marking it safe to replace. Reason: {0}'.format(should_process_reason))
                        self.flag_kodi_clean_library()

            # Check if the processed file season is already in our indexer. If not,
            # the file is most probably mislabled/fake and will be skipped.
            # Only proceed if the file season is > 0
            if int(ep_obj.season) > 0:
                main_db_con = db.DBConnection()
                max_season = main_db_con.select(
                    "SELECT MAX(season) FROM tv_episodes WHERE showid = ? and indexer = ?",
                    [show.indexerid, show.indexer])

                # If the file season (ep_obj.season) is bigger than
                # the indexer season (max_season[0][0]), skip the file
                if int(ep_obj.season) > int(max_season[0][0]):
                    self._log(u'File has season {0}, while the indexer is on season {1}. '
                              u'The file may be incorrectly labeled or fake, aborting.'.format
                              (ep_obj.season, max_season[0][0]))
                    return False

        # if the file is priority then we're going to replace it even if it exists
        else:
            # Set to clean Kodi if file exists and it is priority_download
            if existing_file_status != PostProcessor.DOESNT_EXIST:
                self.flag_kodi_clean_library()
            self._log(u"This download is marked a priority download so I'm going to replace "
                      u"an existing file if I find one")

        # try to find out if we have enough space to perform the copy or move action.
        if not helpers.is_file_locked(self.file_path, False):
            if not verify_freespace(self.file_path, ep_obj.show._location, [ep_obj] + ep_obj.related_episodes):
                self._log(u'Not enough space to continue post-processing, exiting', logger.WARNING)
                return False
        else:
            self._log(u'Unable to determine needed filespace as the source file is locked for access')

        # delete the existing file (and company)
        for cur_ep in [ep_obj] + ep_obj.related_episodes:
            try:
                self._delete(cur_ep.location, associated_files=True)
                # clean up any left over folders
                if cur_ep.location:
                    helpers.delete_empty_folders(os.path.dirname(cur_ep.location), keep_dir=ep_obj.show._location)
            except (OSError, IOError):
                raise EpisodePostProcessingFailedException(u'Unable to delete the existing files')

            # set the status of the episodes
            # for cur_ep in [ep_obj] + ep_obj.related_episodes:
            #    cur_ep.status = common.Quality.composite_status(common.SNATCHED, new_ep_quality)

        # if the show directory doesn't exist then make it if desired
        if not os.path.isdir(ep_obj.show._location) and app.CREATE_MISSING_SHOW_DIRS:
            self._log(u"Show directory doesn't exist, creating it", logger.DEBUG)
            try:
                os.mkdir(ep_obj.show._location)
                helpers.chmod_as_parent(ep_obj.show._location)

                # do the library update for synoindex
                notifiers.synoindex_notifier.addFolder(ep_obj.show._location)
            except (OSError, IOError):
                raise EpisodePostProcessingFailedException(u'Unable to create the show directory: {0}'.format
                                                           (ep_obj.show._location))

            # get metadata for the show (but not episode because it hasn't been fully processed)
            ep_obj.show.write_metadata(True)

        # update the ep info before we rename so the quality & release name go into the name properly
        sql_l = []

        for cur_ep in [ep_obj] + ep_obj.related_episodes:
            with cur_ep.lock:

                if self.release_name:
                    self._log(u'Found release name {0}'.format(self.release_name), logger.DEBUG)
                    cur_ep.release_name = self.release_name
                elif self.file_name:
                    # If we can't get the release name we expect, save the original release name instead
                    self._log(u'Using original release name {0}'.format(self.file_name), logger.DEBUG)
                    cur_ep.release_name = self.file_name
                else:
                    cur_ep.release_name = u''

                cur_ep.status = common.Quality.composite_status(common.DOWNLOADED, new_ep_quality)

                cur_ep.subtitles = u''

                cur_ep.subtitles_searchcount = 0

                cur_ep.subtitles_lastsearch = u'0001-01-01 00:00:00'

                cur_ep.is_proper = self.is_proper

                cur_ep.version = new_ep_version

                if self.release_group:
                    cur_ep.release_group = self.release_group
                else:
                    cur_ep.release_group = u''

                sql_l.append(cur_ep.get_sql())

        # Just want to keep this consistent for failed handling right now
        nzb_release_name = show_name_helpers.determineReleaseName(self.folder_path, self.nzb_name)
        if nzb_release_name is not None:
            failed_history.log_success(nzb_release_name)
        else:
            self._log(u"Couldn't determine NZB release name, aborting", logger.WARNING)

        # find the destination folder
        try:
            proper_path = ep_obj.proper_path()
            proper_absolute_path = os.path.join(ep_obj.show.location, proper_path)
            dest_path = os.path.dirname(proper_absolute_path)
        except ShowDirectoryNotFoundException:
            raise EpisodePostProcessingFailedException(u"Unable to post-process an episode if the show dir '{0}' "
                                                       u"doesn't exist, quitting".format(ep_obj.show.raw_location))

        self._log(u'Destination folder for this episode: {0}'.format(dest_path), logger.DEBUG)

        # create any folders we need
        if not helpers.make_dirs(dest_path):
            raise EpisodePostProcessingFailedException('Unable to create destination folder to the files')

        # figure out the base name of the resulting episode file
        if app.RENAME_EPISODES:
            orig_extension = self.file_name.rpartition('.')[-1]
            new_base_name = os.path.basename(proper_path)
            new_file_name = new_base_name + '.' + orig_extension

        else:
            # if we're not renaming then there's no new base name, we'll just use the existing name
            new_base_name = None
            new_file_name = self.file_name

        # add to anidb
        if ep_obj.show.is_anime and app.ANIDB_USE_MYLIST:
            self._add_to_anidb_mylist(self.file_path)

        try:
            # do the action to the episode and associated files to the show dir
            if self.process_method in ['copy', 'hardlink', 'move', 'symlink']:
                if not self.process_method == 'hardlink':
                    if helpers.is_file_locked(self.file_path, False):
                        raise EpisodePostProcessingFailedException('File is locked for reading')
                self.post_process_action(self.file_path, dest_path, new_base_name,
                                         app.MOVE_ASSOCIATED_FILES, app.USE_SUBTITLES and ep_obj.show.subtitles)
            else:
                logger.log(u"'{0}' is an unknown file processing method. "
                           u"Please correct your app's usage of the API.".format(self.process_method), logger.WARNING)
                raise EpisodePostProcessingFailedException('Unable to move the files to their new home')
        except (OSError, IOError):
            raise EpisodePostProcessingFailedException('Unable to move the files to their new home')

        # download subtitles
        if app.USE_SUBTITLES and ep_obj.show.subtitles:
            for cur_ep in [ep_obj] + ep_obj.related_episodes:
                with cur_ep.lock:
                    cur_ep.location = os.path.join(dest_path, new_file_name)
                    cur_ep.refresh_subtitles()
                    cur_ep.download_subtitles()

        # now that processing has finished, we can put the info in the DB.
        # If we do it earlier, then when processing fails, it won't try again.
        if sql_l:
            main_db_con = db.DBConnection()
            main_db_con.mass_action(sql_l)

        # put the new location in the database
        sql_l = []
        for cur_ep in [ep_obj] + ep_obj.related_episodes:
            with cur_ep.lock:
                cur_ep.location = os.path.join(dest_path, new_file_name)
                sql_l.append(cur_ep.get_sql())

        if sql_l:
            main_db_con = db.DBConnection()
            main_db_con.mass_action(sql_l)

        cur_ep.airdate_modify_stamp()

        # generate nfo/tbn
        try:
            ep_obj.create_meta_files()
        except Exception:
            logger.log(u'Could not create/update meta files. Continuing with post-processing...')

        # log it to history episode and related episodes (multi-episode for example)
        for cur_ep in [ep_obj] + ep_obj.related_episodes:
            history.logDownload(cur_ep, self.file_path, new_ep_quality, self.release_group, new_ep_version)

        # send notifications
        notifiers.notify_download(ep_obj._format_pattern('%SN - %Sx%0E - %EN - %QN'))
        # do the library update for KODI
        notifiers.kodi_notifier.update_library(ep_obj.show.name)
        # do the library update for Plex
        notifiers.plex_notifier.update_library(ep_obj)
        # do the library update for EMBY
        notifiers.emby_notifier.update_library(ep_obj.show)
        # do the library update for NMJ
        # nmj_notifier kicks off its library update when the notify_download is issued (inside notifiers)
        # do the library update for Synology Indexer
        notifiers.synoindex_notifier.addFile(ep_obj.location)
        # do the library update for pyTivo
        notifiers.pytivo_notifier.update_library(ep_obj)
        # do the library update for Trakt
        notifiers.trakt_notifier.update_library(ep_obj)

        self._run_extra_scripts(ep_obj)

        if app.USE_TORRENTS and app.PROCESS_METHOD in ('hardlink', 'symlink') and app.TORRENT_SEED_LOCATION:
            if not os.path.isdir(app.TORRENT_SEED_LOCATION):
                logger.log('Not possible to move torrent after Post-Processor because seed location is invalid',
                           logger.WARNING)
            elif not self.info_hash:
                logger.log("Not possible to move torrent after Post-Processor because info hash wasn't found in history",
                           logger.WARNING)
            else:
                logger.log('Trying to move torrent after Post-Processor', logger.DEBUG)
                client = torrent.get_client_class(app.TORRENT_METHOD)()
                try:
                    torrent_moved = client.move_torrent(self.info_hash)
                except (requests.exceptions.RequestException, socket.gaierror) as e:
                    logger.log("Could't connect to client to move '{release}' torrent with hash: {hash} to: '{path}'. "
                               "Error: {error}".format(release=self.release_name, hash=self.info_hash, error=e.message,
                                                       path=app.TORRENT_SEED_LOCATION), logger.WARNING)
                except AttributeError:
                    logger.log("Your client doesn't support moving torrents to new location", logger.WARNING)

                if torrent_moved:
                    logger.log("Moved torrent from '{release}' with hash: {hash} to: '{path}'".format
                               (release=self.release_name, hash=self.info_hash, path=app.TORRENT_SEED_LOCATION),
                               logger.WARNING)
                else:
                    logger.log("Could not move '{release}' torrent with hash: {hash} to: '{path}'. "
                               "Please check logs.".format(release=self.release_name, hash=self.info_hash,
                                                           path=app.TORRENT_SEED_LOCATION), logger.WARNING)

        return True