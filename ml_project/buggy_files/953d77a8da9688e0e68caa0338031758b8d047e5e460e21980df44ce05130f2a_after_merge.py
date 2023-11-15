    def process(self):  # pylint: disable=too-many-return-statements, too-many-locals, too-many-branches, too-many-statements
        """
        Post-process a given file

        :return: True on success, False on failure
        """

        self._log(u"Processing " + self.file_path + " (" + str(self.nzb_name) + ")")

        if ek(os.path.isdir, self.file_path):
            self._log(u"File {0} seems to be a directory".format(self.file_path))
            return False

        if not ek(os.path.exists, self.file_path):
            self._log(u"File {0} doesn't exist, did unrar fail?".format(self.file_path))
            return False

        for ignore_file in self.IGNORED_FILESTRINGS:
            if ignore_file in self.file_path:
                self._log(u"File {0} is ignored type, skipping".format(self.file_path))
                return False

        # reset per-file stuff
        self.in_history = False

        # reset the anidb episode object
        self.anidbEpisode = None

        # try to find the file info
        (show, season, episodes, quality, version) = self._find_info()
        if not show:
            self._log(u"This show isn't in your list, you need to add it to SR before post-processing an episode")
            raise EpisodePostProcessingFailedException()
        elif season is None or not episodes:
            self._log(u"Not enough information to determine what episode this is. Quitting post-processing")
            return False

        # retrieve/create the corresponding TVEpisode objects
        ep_obj = self._get_ep_obj(show, season, episodes)
        _, old_ep_quality = common.Quality.splitCompositeStatus(ep_obj.status)

        # get the quality of the episode we're processing
        if quality and not common.Quality.qualityStrings[quality] == 'Unknown':
            self._log(u"Snatch history had a quality in it, using that: " + common.Quality.qualityStrings[quality],
                      logger.DEBUG)
            new_ep_quality = quality
        else:
            new_ep_quality = self._get_quality(ep_obj)

        logger.log(u"Quality of the episode we're processing: {0}".format(common.Quality.qualityStrings[new_ep_quality]), logger.DEBUG)

        # see if this is a priority download (is it snatched, in history, PROPER, or BEST)
        priority_download = self._is_priority(ep_obj, new_ep_quality)
        self._log(u"Is ep a priority download: " + str(priority_download), logger.DEBUG)

        # get the version of the episode we're processing
        if version:
            self._log(u"Snatch history had a version in it, using that: v" + str(version),
                      logger.DEBUG)
            new_ep_version = version
        else:
            new_ep_version = -1

        # check for an existing file
        existing_file_status = self._checkForExistingFile(ep_obj.location)

        if not priority_download:
            if existing_file_status == PostProcessor.EXISTS_SAME:
                self._log(u"File exists and new file is same size, pretending we did something")
                return True

            if new_ep_quality <= old_ep_quality and old_ep_quality != common.Quality.UNKNOWN and existing_file_status != PostProcessor.DOESNT_EXIST:
                if self.is_proper and new_ep_quality == old_ep_quality:
                    self._log(u"New file is a proper/repack, marking it safe to replace")
                else:
                    _, preferred_qualities = common.Quality.splitQuality(int(show.quality))
                    if new_ep_quality not in preferred_qualities:
                        self._log(u"File exists and new file quality is not in a preferred quality list, marking it unsafe to replace")
                        return False

            # Check if the processed file season is already in our indexer. If not, the file is most probably mislabled/fake and will be skipped
            # Only proceed if the file season is > 0
            if int(ep_obj.season) > 0:
                main_db_con = db.DBConnection()
                max_season = main_db_con.select(
                    "SELECT MAX(season) FROM tv_episodes WHERE showid = ? and indexer = ?", [show.indexerid, show.indexer])

                if not isinstance(max_season[0][0], int) or max_season[0][0] < 0:
                    self._log(
                        u"File has season {0}, while the database does not have any known seasons yet. "
                        u"Try forcing a full update on the show and process this file again. "
                        u"The file may be incorrectly labeled or fake, aborting.".format(ep_obj.season)
                    )
                    return False

                # If the file season (ep_obj.season) is bigger than the indexer season (max_season[0][0]), skip the file
                if int(ep_obj.season) > max_season[0][0]:
                    self._log(u"File has season {0}, while the indexer is on season {1}. "
                              u"Try forcing a full update on the show and process this file again. "
                              u"The file may be incorrectly labeled or fake, aborting.".format(ep_obj.season, max_season[0][0]))
                    return False

        # if the file is priority then we're going to replace it even if it exists
        else:
            self._log(
                u"This download is marked a priority download so I'm going to replace an existing file if I find one")

        # try to find out if we have enough space to perform the copy or move action.
        if not helpers.isFileLocked(self.file_path, False):
            if not verify_freespace(self.file_path, ep_obj.show._location, [ep_obj] + ep_obj.relatedEps):  # pylint: disable=protected-access
                self._log("Not enough space to continue PP, exiting", logger.WARNING)
                return False
        else:
            self._log("Unable to determine needed filespace as the source file is locked for access")

        # delete the existing file (and company)
        for cur_ep in [ep_obj] + ep_obj.relatedEps:
            try:
                self._delete(cur_ep.location, associated_files=True)

                # clean up any left over folders
                if cur_ep.location:
                    helpers.delete_empty_folders(ek(os.path.dirname, cur_ep.location), keep_dir=ep_obj.show._location)  # pylint: disable=protected-access
            except (OSError, IOError):
                raise EpisodePostProcessingFailedException("Unable to delete the existing files")

            # set the status of the episodes
            # for curEp in [ep_obj] + ep_obj.relatedEps:
            #    curEp.status = common.Quality.compositeStatus(common.SNATCHED, new_ep_quality)

        # if the show directory doesn't exist then make it if allowed
        if not ek(os.path.isdir, ep_obj.show._location) and sickbeard.CREATE_MISSING_SHOW_DIRS:  # pylint: disable=protected-access
            self._log(u"Show directory doesn't exist, creating it", logger.DEBUG)
            try:
                ek(os.mkdir, ep_obj.show._location)  # pylint: disable=protected-access
                helpers.chmodAsParent(ep_obj.show._location)  # pylint: disable=protected-access

                # do the library update for synoindex
                notifiers.synoindex_notifier.addFolder(ep_obj.show._location)  # pylint: disable=protected-access
            except (OSError, IOError):
                raise EpisodePostProcessingFailedException("Unable to create the show directory: " + ep_obj.show._location)  # pylint: disable=protected-access

            # get metadata for the show (but not episode because it hasn't been fully processed)
            ep_obj.show.writeMetadata(True)

        # update the ep info before we rename so the quality & release name go into the name properly
        sql_l = []

        for cur_ep in [ep_obj] + ep_obj.relatedEps:
            with cur_ep.lock:

                if self.release_name:
                    self._log("Found release name " + self.release_name, logger.DEBUG)
                    cur_ep.release_name = self.release_name
                elif self.file_name:
                    # If we can't get the release name we expect, save the original release name instead
                    self._log("Using original release name " + self.file_name, logger.DEBUG)
                    cur_ep.release_name = self.file_name
                else:
                    cur_ep.release_name = ""

                cur_ep.status = common.Quality.compositeStatus(common.DOWNLOADED, new_ep_quality)

                cur_ep.subtitles = u''

                cur_ep.subtitles_searchcount = 0

                cur_ep.subtitles_lastsearch = '0001-01-01 00:00:00'

                cur_ep.is_proper = self.is_proper

                cur_ep.version = new_ep_version

                if self.release_group:
                    cur_ep.release_group = self.release_group
                else:
                    cur_ep.release_group = ""

                sql_l.append(cur_ep.get_sql())

        # Just want to keep this consistent for failed handling right now
        releaseName = show_name_helpers.determineReleaseName(self.folder_path, self.nzb_name)
        if releaseName is not None:
            failed_history.logSuccess(releaseName)
        else:
            self._log(u"Couldn't find release in snatch history", logger.WARNING)

        # find the destination folder
        try:
            proper_path = ep_obj.proper_path()
            proper_absolute_path = ek(os.path.join, ep_obj.show.location, proper_path)

            dest_path = ek(os.path.dirname, proper_absolute_path)
        except ShowDirectoryNotFoundException:
            raise EpisodePostProcessingFailedException(
                u"Unable to post-process an episode if the show dir doesn't exist, quitting")

        self._log(u"Destination folder for this episode: " + dest_path, logger.DEBUG)

        # create any folders we need
        helpers.make_dirs(dest_path)

        # figure out the base name of the resulting episode file
        if sickbeard.RENAME_EPISODES:
            orig_extension = self.file_name.rpartition('.')[-1]
            new_base_name = ek(os.path.basename, proper_path)
            new_file_name = new_base_name + '.' + orig_extension

        else:
            # if we're not renaming then there's no new base name, we'll just use the existing name
            new_base_name = None
            new_file_name = self.file_name

        # add to anidb
        if ep_obj.show.is_anime and sickbeard.ANIDB_USE_MYLIST:
            self._add_to_anidb_mylist(self.file_path)

        try:
            # move the episode and associated files to the show dir
            if self.process_method == "copy":
                if helpers.isFileLocked(self.file_path, False):
                    raise EpisodePostProcessingFailedException("File is locked for reading")
                self._copy(self.file_path, dest_path, new_base_name, sickbeard.MOVE_ASSOCIATED_FILES,
                           sickbeard.USE_SUBTITLES and ep_obj.show.subtitles)
            elif self.process_method == "move":
                if helpers.isFileLocked(self.file_path, True):
                    raise EpisodePostProcessingFailedException("File is locked for reading/writing")
                self._move(self.file_path, dest_path, new_base_name, sickbeard.MOVE_ASSOCIATED_FILES,
                           sickbeard.USE_SUBTITLES and ep_obj.show.subtitles)
            elif self.process_method == "hardlink":
                self._hardlink(self.file_path, dest_path, new_base_name, sickbeard.MOVE_ASSOCIATED_FILES,
                               sickbeard.USE_SUBTITLES and ep_obj.show.subtitles)
            elif self.process_method == "symlink":
                if helpers.isFileLocked(self.file_path, True):
                    raise EpisodePostProcessingFailedException("File is locked for reading/writing")
                self._moveAndSymlink(self.file_path, dest_path, new_base_name, sickbeard.MOVE_ASSOCIATED_FILES,
                                     sickbeard.USE_SUBTITLES and ep_obj.show.subtitles)
            else:
                logger.log(u"Unknown process method: " + str(self.process_method), logger.ERROR)
                raise EpisodePostProcessingFailedException("Unable to move the files to their new home")
        except (OSError, IOError):
            raise EpisodePostProcessingFailedException("Unable to move the files to their new home")

        for cur_ep in [ep_obj] + ep_obj.relatedEps:
            with cur_ep.lock:
                cur_ep.location = ek(os.path.join, dest_path, new_file_name)
                # download subtitles
                if sickbeard.USE_SUBTITLES and ep_obj.show.subtitles:
                    cur_ep.refreshSubtitles()
                    cur_ep.download_subtitles(force=True)
                sql_l.append(cur_ep.get_sql())

        # now that processing has finished, we can put the info in the DB. If we do it earlier, then when processing fails, it won't try again.
        if sql_l:
            main_db_con = db.DBConnection()
            main_db_con.mass_action(sql_l)

        ep_obj.airdateModifyStamp()

        # generate nfo/tbn
        try:
            ep_obj.createMetaFiles()
        except Exception:
            logger.log(u"Could not create/update meta files. Continuing with postProcessing...")

        # log it to history
        history.logDownload(ep_obj, self.file_path, new_ep_quality, self.release_group, new_ep_version)

        # If any notification fails, don't stop postProcessor
        try:
            # send notifications
            notifiers.notify_download(ep_obj._format_pattern('%SN - %Sx%0E - %EN - %QN'))  # pylint: disable=protected-access

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
        except Exception:
            logger.log(u"Some notifications could not be sent. Continuing with postProcessing...")

        self._run_extra_scripts(ep_obj)

        return True