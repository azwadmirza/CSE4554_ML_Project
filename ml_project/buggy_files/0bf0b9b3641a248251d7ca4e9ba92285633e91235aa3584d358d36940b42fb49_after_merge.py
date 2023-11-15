    def editShow(self, show=None, location=None, allowed_qualities=None, preferred_qualities=None,
                 exceptions_list=None, flatten_folders=None, paused=None, directCall=False,
                 air_by_date=None, sports=None, dvd_order=None, indexer_lang=None,
                 subtitles=None, rls_ignore_words=None, rls_require_words=None,
                 anime=None, blacklist=None, whitelist=None, scene=None,
                 defaultEpStatus=None, quality_preset=None):
        # @TODO: Replace with PATCH /api/v2/show/{id}

        allowed_qualities = allowed_qualities or []
        preferred_qualities = preferred_qualities or []
        exceptions = exceptions_list or set()

        anidb_failed = False
        errors = []

        if show is None:
            error_string = 'Invalid show ID: {show}'.format(show=show)
            if directCall:
                return [error_string]
            else:
                return self._genericMessage('Error', error_string)

        show_obj = Show.find(app.showList, int(show))

        if not show_obj:
            error_string = 'Unable to find the specified show: {show}'.format(show=show)
            if directCall:
                return [error_string]
            else:
                return self._genericMessage('Error', error_string)

        show_obj.exceptions = get_scene_exceptions(show_obj.indexerid, show_obj.indexer)

        if try_int(quality_preset, None):
            preferred_qualities = []

        if not location and not allowed_qualities and not preferred_qualities and not flatten_folders:
            t = PageTemplate(rh=self, filename='editShow.mako')

            if show_obj.is_anime:
                if not show_obj.release_groups:
                    show_obj.release_groups = BlackAndWhiteList(show_obj.indexerid)
                whitelist = show_obj.release_groups.whitelist
                blacklist = show_obj.release_groups.blacklist

                groups = []
                if helpers.set_up_anidb_connection() and not anidb_failed:
                    try:
                        anime = adba.Anime(app.ADBA_CONNECTION, name=show_obj.name)
                        groups = anime.get_groups()
                    except Exception as msg:
                        ui.notifications.error('Unable to retreive Fansub Groups from AniDB.')
                        logger.log(u'Unable to retreive Fansub Groups from AniDB. Error is {0}'.format(str(msg)), logger.DEBUG)

            with show_obj.lock:
                show = show_obj
                scene_exceptions = get_scene_exceptions(show_obj.indexerid, show_obj.indexer)

            if show_obj.is_anime:
                return t.render(show=show, scene_exceptions=scene_exceptions, groups=groups, whitelist=whitelist,
                                blacklist=blacklist, title='Edit Show', header='Edit Show', controller='home', action='editShow')
            else:
                return t.render(show=show, scene_exceptions=scene_exceptions, title='Edit Show', header='Edit Show',
                                controller='home', action='editShow')

        flatten_folders = not config.checkbox_to_value(flatten_folders)  # UI inverts this value
        dvd_order = config.checkbox_to_value(dvd_order)
        paused = config.checkbox_to_value(paused)
        air_by_date = config.checkbox_to_value(air_by_date)
        scene = config.checkbox_to_value(scene)
        sports = config.checkbox_to_value(sports)
        anime = config.checkbox_to_value(anime)
        subtitles = config.checkbox_to_value(subtitles)

        do_update = False
        if show_obj.lang != indexer_lang:
            msg = (
                '{{status}} {language}'
                ' for {indexer_name} show {show_id}'.format(
                    language=indexer_lang,
                    show_id=show_obj.indexerid,
                    indexer_name=indexerApi(show_obj.indexer).name,
                )
            )
            status = 'Unexpected result when changing language to'
            log_level = logger.WARNING
            language = show_obj.lang
            try:
                do_update = self.check_show_for_language(
                    show_obj,
                    indexer_lang,
                )
            except IndexerShowNotFoundInLanguage:
                status = 'Could not change language to'
            except IndexerException as error:
                status = u'Failed getting show in'
                msg += u' Please try again later. Error: {err}'.format(
                    err=error,
                )
            else:
                language = indexer_lang
                status = 'Changing language to'
                log_level = logger.INFO
            finally:
                indexer_lang = language
                msg = msg.format(status=status)
                if log_level >= logger.WARNING:
                    errors.append(msg)
                logger.log(msg, log_level)

        if scene == show_obj.scene and anime == show_obj.anime:
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
            if exceptions == show_obj.exceptions:
                do_update_exceptions = False
            else:
                do_update_exceptions = True

            with show_obj.lock:
                if anime:
                    if not show_obj.release_groups:
                        show_obj.release_groups = BlackAndWhiteList(show_obj.indexerid)

                    if whitelist:
                        shortwhitelist = short_group_names(whitelist)
                        show_obj.release_groups.set_white_keywords(shortwhitelist)
                    else:
                        show_obj.release_groups.set_white_keywords([])

                    if blacklist:
                        shortblacklist = short_group_names(blacklist)
                        show_obj.release_groups.set_black_keywords(shortblacklist)
                    else:
                        show_obj.release_groups.set_black_keywords([])

        with show_obj.lock:
            new_quality = Quality.combine_qualities([int(q) for q in allowed_qualities], [int(q) for q in preferred_qualities])
            show_obj.quality = new_quality

            # reversed for now
            if bool(show_obj.flatten_folders) != bool(flatten_folders):
                show_obj.flatten_folders = flatten_folders
                try:
                    app.show_queue_scheduler.action.refreshShow(show_obj)
                except CantRefreshShowException as msg:
                    errors.append('Unable to refresh this show: {error}'.format(error=msg))

            show_obj.paused = paused
            show_obj.scene = scene
            show_obj.anime = anime
            show_obj.sports = sports
            show_obj.subtitles = subtitles
            show_obj.air_by_date = air_by_date
            show_obj.default_ep_status = int(defaultEpStatus)

            if not directCall:
                show_obj.lang = indexer_lang
                show_obj.dvd_order = dvd_order
                show_obj.rls_ignore_words = rls_ignore_words.strip()
                show_obj.rls_require_words = rls_require_words.strip()

            # if we change location clear the db of episodes, change it, write to db, and rescan
            old_location = os.path.normpath(show_obj._location)
            new_location = os.path.normpath(location)
            if old_location != new_location:
                logger.log('{old} != {new}'.format(old=old_location, new=new_location), logger.DEBUG)  # pylint: disable=protected-access
                if not os.path.isdir(location) and not app.CREATE_MISSING_SHOW_DIRS:
                    errors.append('New location <tt>{location}</tt> does not exist'.format(location=location))

                # don't bother if we're going to update anyway
                elif not do_update:
                    # change it
                    try:
                        show_obj.location = location
                        try:
                            app.show_queue_scheduler.action.refreshShow(show_obj)
                        except CantRefreshShowException as msg:
                            errors.append('Unable to refresh this show:{error}'.format(error=msg))
                            # grab updated info from TVDB
                            # show_obj.load_episodes_from_indexer()
                            # rescan the episodes in the new folder
                    except ShowDirectoryNotFoundException:
                        errors.append('The folder at <tt>{location}</tt> doesn\'t contain a tvshow.nfo - '
                                      'copy your files to that folder before you change the directory in Medusa.'.format
                                      (location=location))

            # save it to the DB
            show_obj.save_to_db()

        # force the update
        if do_update:
            try:
                app.show_queue_scheduler.action.updateShow(show_obj)
                time.sleep(cpu_presets[app.CPU_PRESET])
            except CantUpdateShowException as msg:
                errors.append('Unable to update show: {0}'.format(str(msg)))

        if do_update_exceptions:
            try:
                update_scene_exceptions(show_obj.indexerid, show_obj.indexer, exceptions)  # @UndefinedVdexerid)
                time.sleep(cpu_presets[app.CPU_PRESET])
            except CantUpdateShowException:
                errors.append('Unable to force an update on scene exceptions of the show.')

        if do_update_scene_numbering:
            try:
                xem_refresh(show_obj.indexerid, show_obj.indexer)
                time.sleep(cpu_presets[app.CPU_PRESET])
            except CantUpdateShowException:
                errors.append('Unable to force an update on scene numbering of the show.')

            # Must erase cached results when toggling scene numbering
            self.erase_cache(show_obj)

        if directCall:
            return errors

        if errors:
            ui.notifications.error(
                '{num} error{s} while saving changes:'.format(num=len(errors), s='s' if len(errors) > 1 else ''),
                '<ul>\n{list}\n</ul>'.format(list='\n'.join(['<li>{items}</li>'.format(items=error_item)
                                                             for error_item in errors])))

        return self.redirect('/home/displayShow?show={show}'.format(show=show))