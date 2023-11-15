    def delete_show(self, full=False):
        """Delete the tv show from the database.

        :param full:
        :type full: bool
        """
        sql_l = [[b'DELETE FROM tv_episodes WHERE showid = ?', [self.indexerid]],
                 [b'DELETE FROM tv_shows WHERE indexer_id = ?', [self.indexerid]],
                 [b'DELETE FROM imdb_info WHERE indexer_id = ?', [self.indexerid]],
                 [b'DELETE FROM xem_refresh WHERE indexer_id = ?', [self.indexerid]],
                 [b'DELETE FROM scene_numbering WHERE indexer_id = ?', [self.indexerid]]]

        main_db_con = db.DBConnection()
        main_db_con.mass_action(sql_l)

        action = ('delete', 'trash')[sickbeard.TRASH_REMOVE_SHOW]

        # remove self from show list
        sickbeard.showList = [x for x in sickbeard.showList if int(x.indexerid) != self.indexerid]

        # clear the cache
        image_cache_dir = ek(os.path.join, sickbeard.CACHE_DIR, 'images')
        for cache_file in ek(glob.glob, ek(os.path.join, image_cache_dir, str(self.indexerid) + '.*')):
            logger.log(u'Attempt to %s cache file %s' % (action, cache_file))
            try:
                if sickbeard.TRASH_REMOVE_SHOW:
                    send2trash(cache_file)
                else:
                    ek(os.remove, cache_file)

            except OSError as e:
                logger.log(u'Unable to %s %s: %s / %s' % (action, cache_file, repr(e), str(e)), logger.WARNING)

        # remove entire show folder
        if full:
            try:
                logger.log(u'Attempt to %s show folder %s' % (action, self.location))
                # check first the read-only attribute
                file_attribute = ek(os.stat, self.location)[0]
                if not file_attribute & stat.S_IWRITE:
                    # File is read-only, so make it writeable
                    logger.log(u'Attempting to make writeable the read only folder %s' % self.location, logger.DEBUG)
                    try:
                        ek(os.chmod, self.location, stat.S_IWRITE)
                    except Exception:
                        logger.log(u'Unable to change permissions of %s' % self.location, logger.WARNING)

                if sickbeard.TRASH_REMOVE_SHOW:
                    send2trash(self.location)
                else:
                    ek(shutil.rmtree, self.location)

                logger.log(u'%s show folder %s' % (('Deleted', 'Trashed')[sickbeard.TRASH_REMOVE_SHOW], self.raw_location))

            except ShowDirectoryNotFoundException:
                logger.log(u'Show folder does not exist, no need to %s %s' % (action, self.raw_location), logger.WARNING)
            except OSError as e:
                logger.log(u'Unable to %s %s: %s / %s' % (action, self.raw_location, repr(e), str(e)), logger.WARNING)

        if sickbeard.USE_TRAKT and sickbeard.TRAKT_SYNC_WATCHLIST:
            logger.log(u'Removing show: indexerid ' + str(self.indexerid) +
                       u', Title ' + str(self.name) + u' from Watchlist', logger.DEBUG)
            notifiers.trakt_notifier.update_watchlist(self, update='remove')