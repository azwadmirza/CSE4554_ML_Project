    def editShow(self, indexername=None, seriesid=None, location=None, allowed_qualities=None, preferred_qualities=None,
                 exceptions_list=None, season_folders=None, paused=None, directCall=False,
                 air_by_date=None, sports=None, dvd_order=None, indexer_lang=None,
                 subtitles=None, rls_ignore_words=None, rls_require_words=None,
                 anime=None, blacklist=None, whitelist=None, scene=None,
                 defaultEpStatus=None, quality_preset=None):

        allowed_qualities = allowed_qualities or []
        preferred_qualities = preferred_qualities or []
        exceptions = exceptions_list or set()

        anidb_failed = False
        errors = 0

        if not indexername or not seriesid:
            error_string = 'No show was selected'
            if directCall:
                errors += 1
                return errors
            else:
                return self._genericMessage('Error', error_string)

        series_obj = Show.find_by_id(app.showList, indexer_name_to_id(indexername), seriesid)

        if not series_obj:
            error_string = 'Unable to find the specified show ID: {show}'.format(show=series_obj)
            if directCall:
                errors += 1
                return errors
            else:
                return self._genericMessage('Error', error_string)

        series_obj.exceptions = get_scene_exceptions(series_obj)

        # If user set quality_preset remove all preferred_qualities
        if try_int(quality_preset, None):
            preferred_qualities = []

        if not location and not allowed_qualities and not preferred_qualities and season_folders is None:
            t = PageTemplate(rh=self, filename='editShow.mako')

            if series_obj.is_anime:
                if not series_obj.release_groups:
                    series_obj.release_groups = BlackAndWhiteList(series_obj)
                whitelist = series_obj.release_groups.whitelist
                blacklist = series_obj.release_groups.blacklist

                groups = []
                if set_up_anidb_connection() and not anidb_failed:
                    try:
                        anime = adba.Anime(app.ADBA_CONNECTION, name=series_obj.name)
                        groups = anime.get_groups()
                    except Exception as e:
                        errors += 1
                        logger.log(u'Unable to retreive Fansub Groups from AniDB. Error:{error}'.format
                                   (error=e.message), logger.WARNING)

            with series_obj.lock:
                show = series_obj
                scene_exceptions = get_scene_exceptions(series_obj)

            if series_obj.is_anime:
                return t.render(show=show, scene_exceptions=scene_exceptions, groups=groups, whitelist=whitelist,
                                blacklist=blacklist, title='Edit Show', header='Edit Show', controller='home',
                                action='editShow')
            else:
                return t.render(show=show, scene_exceptions=scene_exceptions, title='Edit Show', header='Edit Show',
                                controller='home', action='editShow')

        season_folders = config.checkbox_to_value(season_folders)
        dvd_order = config.checkbox_to_value(dvd_order)
        paused = config.checkbox_to_value(paused)
        air_by_date = config.checkbox_to_value(air_by_date)
        scene = config.checkbox_to_value(scene)
        sports = config.checkbox_to_value(sports)
        anime = config.checkbox_to_value(anime)
        subtitles = config.checkbox_to_value(subtitles)

        do_update = False
        # In mass edit, we can't change language so we need to check if indexer_lang is set
        if indexer_lang and series_obj.lang != indexer_lang:
            msg = (
                '{{status}} {language}'
                ' for {indexer_name} show {show_id}'.format(
                    language=indexer_lang,
                    show_id=series_obj.indexerid,
                    indexer_name=indexerApi(series_obj.indexer).name,
                )
            )
            status = 'Unexpected result when changing language to'
            log_level = logger.WARNING
            language = series_obj.lang
            try:
                do_update = self.check_show_for_language(
                    series_obj,
                    indexer_lang,
                )
            except IndexerShowNotFoundInLanguage:
                errors += 1
                status = 'Could not change language to'
            except IndexerException as e:
                errors += 1
                status = u'Failed getting show in'
                msg += u' Please try again later. Error: {error}'.format(
                    error=e.message,
                )
            else:
                language = indexer_lang
                status = 'Changing language to'
                log_level = logger.INFO
            finally:
                indexer_lang = language
                msg = msg.format(status=status)
                logger.log(msg, log_level)

        if scene == series_obj.scene and anime == series_obj.anime:
            do_update_scene_numbering = False
        else:
            do_update_scene_numbering = True

        if not isinstance(allowed_qualities, list):
            allowed_qualities = [allowed_qualities]

        if not isinstance(preferred_qualities, list):
            preferred_qualities = [preferred_qualities]

        if isinstance(exceptions, list):
            exceptions = set(exceptions)

        if not isinstance(exceptions, set):
            exceptions = {exceptions}

        # If directCall from mass_edit_update no scene exceptions handling or
        # blackandwhite list handling
        if directCall:
            do_update_exceptions = False
        else:
            if exceptions == series_obj.exceptions:
                do_update_exceptions = False
            else:
                do_update_exceptions = True

            with series_obj.lock:
                if anime:
                    if not series_obj.release_groups:
                        series_obj.release_groups = BlackAndWhiteList(series_obj)

                    if whitelist:
                        shortwhitelist = short_group_names(whitelist)
                        series_obj.release_groups.set_white_keywords(shortwhitelist)
                    else:
                        series_obj.release_groups.set_white_keywords([])

                    if blacklist:
                        shortblacklist = short_group_names(blacklist)
                        series_obj.release_groups.set_black_keywords(shortblacklist)
                    else:
                        series_obj.release_groups.set_black_keywords([])

        with series_obj.lock:
            new_quality = Quality.combine_qualities([int(q) for q in allowed_qualities],
                                                    [int(q) for q in preferred_qualities])
            series_obj.quality = new_quality

            # reversed for now
            if bool(series_obj.season_folders) != bool(season_folders):
                series_obj.season_folders = season_folders
                try:
                    app.show_queue_scheduler.action.refreshShow(series_obj)
                except CantRefreshShowException as e:
                    errors += 1
                    logger.log("Unable to refresh show '{show}': {error}".format
                               (show=series_obj.name, error=e.message), logger.WARNING)

            # Check if we should erase parsed cached results for that show
            do_erase_parsed_cache = False
            for item in [('scene', scene), ('anime', anime), ('sports', sports),
                         ('air_by_date', air_by_date), ('dvd_order', dvd_order)]:
                if getattr(series_obj, item[0]) != item[1]:
                    do_erase_parsed_cache = True
                    # Break if at least one setting was changed
                    break

            series_obj.paused = paused
            series_obj.scene = scene
            series_obj.anime = anime
            series_obj.sports = sports
            series_obj.subtitles = subtitles
            series_obj.air_by_date = air_by_date
            series_obj.default_ep_status = int(defaultEpStatus)
            series_obj.dvd_order = dvd_order

            if not directCall:
                series_obj.lang = indexer_lang
                series_obj.rls_ignore_words = rls_ignore_words.strip()
                series_obj.rls_require_words = rls_require_words.strip()

            # if we change location clear the db of episodes, change it, write to db, and rescan
            old_location = os.path.normpath(series_obj._location)
            new_location = os.path.normpath(location)
            if old_location != new_location:
                changed_location = True
                logger.log('Changing show location to: {new}'.format(new=new_location), logger.INFO)
                if not os.path.isdir(new_location):
                    if app.CREATE_MISSING_SHOW_DIRS:
                        logger.log(u"Show directory doesn't exist, creating it", logger.INFO)
                        try:
                            os.mkdir(new_location)
                        except OSError as error:
                            errors += 1
                            changed_location = False
                            logger.log(u"Unable to create the show directory '{location}'. Error: {msg}".format
                                       (location=new_location, msg=error), logger.WARNING)
                        else:
                            logger.log(u"New show directory created", logger.INFO)
                            helpers.chmod_as_parent(new_location)
                    else:
                        logger.log("New location '{location}' does not exist. "
                                   "Enable setting 'Create missing show dirs'".format
                                   (location=location), logger.WARNING)

                # Save new location to DB only if we changed it
                if changed_location:
                    series_obj.location = new_location

                if (do_update or changed_location) and os.path.isdir(new_location):
                    try:
                        app.show_queue_scheduler.action.refreshShow(series_obj)
                    except CantRefreshShowException as e:
                        errors += 1
                        logger.log("Unable to refresh show '{show}'. Error: {error}".format
                                   (show=series_obj.name, error=e.message), logger.WARNING)

            # Save all settings changed while in series_obj.lock
            series_obj.save_to_db()

        # force the update
        if do_update:
            try:
                app.show_queue_scheduler.action.updateShow(series_obj)
                time.sleep(cpu_presets[app.CPU_PRESET])
            except CantUpdateShowException as e:
                errors += 1
                logger.log("Unable to update show '{show}': {error}".format
                           (show=series_obj.name, error=e.message), logger.WARNING)

        if do_update_exceptions:
            try:
                update_scene_exceptions(series_obj, exceptions)
                time.sleep(cpu_presets[app.CPU_PRESET])
                name_cache.build_name_cache(series_obj)
            except CantUpdateShowException:
                errors += 1
                logger.log("Unable to force an update on scene exceptions for show '{show}': {error}".format
                           (show=series_obj.name, error=e.message), logger.WARNING)

        if do_update_scene_numbering or do_erase_parsed_cache:
            try:
                xem_refresh(series_obj)
                time.sleep(cpu_presets[app.CPU_PRESET])
            except CantUpdateShowException:
                errors += 1
                logger.log("Unable to force an update on scene numbering for show '{show}': {error}".format
                           (show=series_obj.name, error=e.message), logger.WARNING)

            # Must erase cached DB results when toggling scene numbering
            self.erase_cache(series_obj)

            # Erase parsed cached names as we are changing scene numbering
            series_obj.flush_episodes()
            series_obj.erase_cached_parse()

            # Need to refresh show as we updated scene numbering or changed show format
            try:
                app.show_queue_scheduler.action.refreshShow(series_obj)
            except CantRefreshShowException as e:
                errors += 1
                logger.log("Unable to refresh show '{show}'. Please manually trigger a full show refresh. "
                           "Error: {error}".format(show=series_obj.name, error=e.message), logger.WARNING)

        if directCall:
            return errors

        if errors:
            ui.notifications.error(
                'Errors', '{num} error{s} while saving changes. Please check logs'.format(
                    num=errors, s='s' if errors > 1 else ''
                )
            )

        logger.log(u"Finished editing show: {show}".format(show=series_obj.name), logger.DEBUG)
        return self.redirect(
            '/home/displayShow?indexername={series_obj.indexer_name}&seriesid={series_obj.series_id}'.format(
                series_obj=series_obj))