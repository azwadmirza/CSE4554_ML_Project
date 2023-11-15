    def displayShow(self, show=None):
        # TODO: add more comprehensive show validation
        try:
            show = int(show)  # fails if show id ends in a period SickRage/sickrage-issues#65
            show_obj = Show.find(sickbeard.showList, show)
        except (ValueError, TypeError):
            return self._genericMessage('Error', 'Invalid show ID: {show}'.format(show=show))

        if show_obj is None:
            return self._genericMessage('Error', 'Show not in show list')

        main_db_con = db.DBConnection()
        season_results = main_db_con.select(
            b'SELECT DISTINCT season '
            b'FROM tv_episodes '
            b'WHERE showid = ? AND  season IS NOT NULL '
            b'ORDER BY season DESC',
            [show_obj.indexerid]
        )

        min_season = 0 if sickbeard.DISPLAY_SHOW_SPECIALS else 1

        sql_results = main_db_con.select(
            b'SELECT * '
            b'FROM tv_episodes '
            b'WHERE showid = ? AND season >= ? '
            b'ORDER BY season DESC, episode DESC',
            [show_obj.indexerid, min_season]
        )

        t = PageTemplate(rh=self, filename='displayShow.mako')
        submenu = [{
            'title': 'Edit',
            'path': 'home/editShow?show={show}'.format(show=show_obj.indexerid),
            'icon': 'ui-icon ui-icon-pencil',
        }]

        try:
            show_loc = (show_obj.location, True)
        except ShowDirectoryNotFoundException:
            show_loc = (show_obj._location, False)  # pylint: disable=protected-access

        show_message = ''

        if sickbeard.showQueueScheduler.action.isBeingAdded(show_obj):
            show_message = 'This show is in the process of being downloaded - the info below is incomplete.'

        elif sickbeard.showQueueScheduler.action.isBeingUpdated(show_obj):
            show_message = 'The information on this page is in the process of being updated.'

        elif sickbeard.showQueueScheduler.action.isBeingRefreshed(show_obj):
            show_message = 'The episodes below are currently being refreshed from disk'

        elif sickbeard.showQueueScheduler.action.isBeingSubtitled(show_obj):
            show_message = 'Currently downloading subtitles for this show'

        elif sickbeard.showQueueScheduler.action.isInRefreshQueue(show_obj):
            show_message = 'This show is queued to be refreshed.'

        elif sickbeard.showQueueScheduler.action.isInUpdateQueue(show_obj):
            show_message = 'This show is queued and awaiting an update.'

        elif sickbeard.showQueueScheduler.action.isInSubtitleQueue(show_obj):
            show_message = 'This show is queued and awaiting subtitles download.'

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
                    'icon': 'menu-icon-kodi',
                })
                submenu.append({
                    'title': 'Update show in Emby',
                    'path': 'home/updateEMBY?show={show}'.format(show=show_obj.indexerid),
                    'requires': self.haveEMBY(),
                    'icon': 'menu-icon-emby',
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
                        'icon': 'menu-icon-backlog',
                    })

        ep_counts = {
            Overview.SKIPPED: 0,
            Overview.WANTED: 0,
            Overview.QUAL: 0,
            Overview.GOOD: 0,
            Overview.UNAIRED: 0,
            Overview.SNATCHED: 0,
            Overview.SNATCHED_PROPER: 0,
            Overview.SNATCHED_BEST: 0
        }
        ep_cats = {}

        for cur_result in sql_results:
            cur_ep_cat = show_obj.get_overview(cur_result[b'status'])
            if cur_ep_cat:
                ep_cats['{season}x{episode}'.format(season=cur_result[b'season'], episode=cur_result[b'episode'])] = cur_ep_cat
                ep_counts[cur_ep_cat] += 1

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
            sorted_show_lists = [['Shows', sorted(shows, lambda x, y: cmp(titler(x.name), titler(y.name)))],
                               ['Anime', sorted(anime, lambda x, y: cmp(titler(x.name), titler(y.name)))]]
        else:
            sorted_show_lists = [
                ['Shows', sorted(sickbeard.showList, lambda x, y: cmp(titler(x.name), titler(y.name)))]]

        bwl = None
        if show_obj.is_anime:
            bwl = show_obj.release_groups

        show_obj.exceptions = get_scene_exceptions(show_obj.indexerid)

        indexerid = int(show_obj.indexerid)
        indexer = int(show_obj.indexer)

        # Delete any previous occurrances
        for index, recentShow in enumerate(sickbeard.SHOWS_RECENT):
            if recentShow['indexerid'] == indexerid:
                del sickbeard.SHOWS_RECENT[index]

        # Only track 5 most recent shows
        del sickbeard.SHOWS_RECENT[4:]

        # Insert most recent show
        sickbeard.SHOWS_RECENT.insert(0, {
            'indexerid': indexerid,
            'name': show_obj.name,
        })

        show_words = show_name_helpers.show_words(show_obj)

        return t.render(
            submenu=submenu, showLoc=show_loc, show_message=show_message,
            show=show_obj, sql_results=sql_results, seasonResults=season_results,
            sortedShowLists=sorted_show_lists, bwl=bwl, epCounts=ep_counts,
            epCats=ep_cats, all_scene_exceptions=' | '.join(show_obj.exceptions),
            scene_numbering=get_scene_numbering_for_show(indexerid, indexer),
            xem_numbering=get_xem_numbering_for_show(indexerid, indexer),
            scene_absolute_numbering=get_scene_absolute_numbering_for_show(indexerid, indexer),
            xem_absolute_numbering=get_xem_absolute_numbering_for_show(indexerid, indexer),
            title=show_obj.name,
            controller='home',
            action='displayShow',
            preferred_words=show_words.preferred_words,
            undesired_words=show_words.undesired_words,
            ignore_words=show_words.ignore_words,
            require_words=show_words.require_words
        )