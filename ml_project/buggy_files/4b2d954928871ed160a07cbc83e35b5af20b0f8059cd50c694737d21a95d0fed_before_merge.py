    def snatchSelection(self, show=None, season=None, episode=None, manual_search_type='episode',
                        perform_search=0, down_cur_quality=0, show_all_results=0):
        """ The view with results for the manual selected show/episode """

        indexer_tvdb = 1
        # TODO: add more comprehensive show validation
        try:
            show = int(show)  # fails if show id ends in a period SickRage/sickrage-issues#65
            show_obj = Show.find(sickbeard.showList, show)
        except (ValueError, TypeError):
            return self._genericMessage('Error', 'Invalid show ID: {show}'.format(show=show))

        if show_obj is None:
            return self._genericMessage('Error', 'Show not in show list')

        # Retrieve cache results from providers
        search_show = {'show': show, 'season': season, 'episode': episode, 'manual_search_type': manual_search_type}

        provider_results = get_provider_cache_results(indexer_tvdb, perform_search=perform_search,
                                                      show_all_results=show_all_results, **search_show)

        t = PageTemplate(rh=self, filename='snatchSelection.mako')
        submenu = [{
            'title': 'Edit',
            'path': 'home/editShow?show={show}'.format(show=show_obj.indexerid),
            'icon': 'ui-icon ui-icon-pencil'
        }]

        try:
            show_loc = (show_obj.location, True)
        except ShowDirectoryNotFoundException:
            show_loc = (show_obj._location, False)  # pylint: disable=protected-access

        show_message = sickbeard.showQueueScheduler.action.getQueueActionMessage(show_obj)

        if not sickbeard.showQueueScheduler.action.isBeingAdded(show_obj):
            if not sickbeard.showQueueScheduler.action.isBeingUpdated(show_obj):
                submenu.append({
                    'title': 'Resume' if show_obj.paused else 'Pause',
                    'path': 'home/togglePause?show={show}'.format(show=show_obj.indexerid),
                    'icon': 'ui-icon ui-icon-{state}'.format(state='play' if show_obj.paused else 'pause'),
                })
                submenu.append({
                    'title': 'Remove',
                    'path': 'home/delete_show?show={show}'.format(show=show_obj.indexerid),
                    'class': 'removeshow',
                    'confirm': True,
                    'icon': 'ui-icon ui-icon-trash',
                })
                submenu.append({
                    'title': 'Re-scan files',
                    'path': 'home/refreshShow?show={show}'.format(show=show_obj.indexerid),
                    'icon': 'ui-icon ui-icon-refresh',
                })
                submenu.append({
                    'title': 'Force Full Update',
                    'path': 'home/updateShow?show={show}&amp;force=1'.format(show=show_obj.indexerid),
                    'icon': 'ui-icon ui-icon-transfer-e-w',
                })
                submenu.append({
                    'title': 'Update show in KODI',
                    'path': 'home/updateKODI?show={show}'.format(show=show_obj.indexerid),
                    'requires': self.haveKODI(),
                    'icon': 'submenu-icon-kodi',
                })
                submenu.append({
                    'title': 'Update show in Emby',
                    'path': 'home/updateEMBY?show={show}'.format(show=show_obj.indexerid),
                    'requires': self.haveEMBY(),
                    'icon': 'ui-icon ui-icon-refresh',
                })
                submenu.append({
                    'title': 'Preview Rename',
                    'path': 'home/testRename?show={show}'.format(show=show_obj.indexerid),
                    'icon': 'ui-icon ui-icon-tag',
                })

                if sickbeard.USE_SUBTITLES and not sickbeard.showQueueScheduler.action.isBeingSubtitled(
                        show_obj) and show_obj.subtitles:
                    submenu.append({
                        'title': 'Download Subtitles',
                        'path': 'home/subtitleShow?show={show}'.format(show=show_obj.indexerid),
                        'icon': 'ui-icon ui-icon-comment',
                    })

        def titler(x):
            return (helpers.remove_article(x), x)[not x or sickbeard.SORT_ARTICLE]

        if sickbeard.ANIME_SPLIT_HOME:
            shows = []
            anime = []
            for show in sickbeard.showList:
                if show.is_anime:
                    anime.append(show)
                else:
                    shows.append(show)
            sorted_show_lists = [
                ['Shows', sorted(shows, lambda x, y: cmp(titler(x.name), titler(y.name)))],
                ['Anime', sorted(anime, lambda x, y: cmp(titler(x.name), titler(y.name)))]]
        else:
            sorted_show_lists = [
                ['Shows', sorted(sickbeard.showList, lambda x, y: cmp(titler(x.name), titler(y.name)))]]

        bwl = None
        if show_obj.is_anime:
            bwl = show_obj.release_groups

        show_obj.exceptions = get_scene_exceptions(show_obj.indexerid)

        indexer_id = int(show_obj.indexerid)
        indexer = int(show_obj.indexer)

        # Delete any previous occurrances
        for index, recentShow in enumerate(sickbeard.SHOWS_RECENT):
            if recentShow['indexerid'] == indexer_id:
                del sickbeard.SHOWS_RECENT[index]

        # Only track 5 most recent shows
        del sickbeard.SHOWS_RECENT[4:]

        # Insert most recent show
        sickbeard.SHOWS_RECENT.insert(0, {
            'indexerid': indexer_id,
            'name': show_obj.name,
        })

        episode_history = []
        try:
            main_db_con = db.DBConnection()
            episode_status_result = main_db_con.action(
                b'SELECT date, action, provider, resource '
                b'FROM history '
                b'WHERE showid = ? '
                b'AND season = ? '
                b'AND episode = ? '
                b'AND (action LIKE \'%02\' OR action LIKE \'%04\' OR action LIKE \'%09\' OR action LIKE \'%11\' OR action LIKE \'%12\') '
                b'ORDER BY date DESC',
                [indexer_id, season, episode]
            )
            if episode_status_result:
                for item in episode_status_result:
                    episode_history.append(dict(item))
        except Exception as msg:
            logger.log("Couldn't read latest episode status. Error: {error}".format(error=msg))

        show_words = show_name_helpers.show_words(show_obj)

        return t.render(
            submenu=submenu, showLoc=show_loc, show_message=show_message,
            show=show_obj, provider_results=provider_results, episode=episode,
            sortedShowLists=sorted_show_lists, bwl=bwl, season=season, manual_search_type=manual_search_type,
            all_scene_exceptions=show_obj.exceptions,
            scene_numbering=get_scene_numbering_for_show(indexer_id, indexer),
            xem_numbering=get_xem_numbering_for_show(indexer_id, indexer),
            scene_absolute_numbering=get_scene_absolute_numbering_for_show(indexer_id, indexer),
            xem_absolute_numbering=get_xem_absolute_numbering_for_show(indexer_id, indexer),
            title=show_obj.name,
            controller='home',
            action='snatchSelection',
            preferred_words=show_words.preferred_words,
            undesired_words=show_words.undesired_words,
            ignore_words=show_words.ignore_words,
            require_words=show_words.require_words,
            episode_history=episode_history
        )