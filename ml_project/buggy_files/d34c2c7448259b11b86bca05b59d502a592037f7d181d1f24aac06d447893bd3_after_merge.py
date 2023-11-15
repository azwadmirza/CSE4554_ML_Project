def snatch_episode(result):
    """
    Internal logic necessary to actually "snatch" a result that has been found.

    :param result: SearchResult instance to be snatched.
    :return: boolean, True on success
    """
    if result is None:
        return False

    result.priority = 0  # -1 = low, 0 = normal, 1 = high
    is_proper = False
    if app.ALLOW_HIGH_PRIORITY:
        # if it aired recently make it high priority
        for cur_ep in result.episodes:
            if datetime.date.today() - cur_ep.airdate <= datetime.timedelta(days=7):
                result.priority = 1
    if result.proper_tags:
        logger.log(u'Found proper tags for {0}. Snatching as PROPER'.format(result.name), logger.DEBUG)
        is_proper = True
        end_status = SNATCHED_PROPER
    else:
        end_status = SNATCHED

    if result.url.startswith('magnet') or result.url.endswith('torrent'):
        result.resultType = 'torrent'

    # NZBs can be sent straight to SAB or saved to disk
    if result.resultType in ("nzb", "nzbdata"):
        if app.NZB_METHOD == "blackhole":
            result_downloaded = _download_result(result)
        elif app.NZB_METHOD == "sabnzbd":
            result_downloaded = sab.sendNZB(result)
        elif app.NZB_METHOD == "nzbget":
            result_downloaded = nzbget.sendNZB(result, is_proper)
        else:
            logger.log(u"Unknown NZB action specified in config: " + app.NZB_METHOD, logger.ERROR)
            result_downloaded = False

    # Torrents can be sent to clients or saved to disk
    elif result.resultType == "torrent":
        # torrents are saved to disk when blackhole mode
        if app.TORRENT_METHOD == "blackhole":
            result_downloaded = _download_result(result)
        else:
            if not result.content and not result.url.startswith('magnet'):
                if result.provider.login():
                    result.content = result.provider.get_url(result.url, returns='content')

            if result.content or result.url.startswith('magnet'):
                client = torrent.get_client_class(app.TORRENT_METHOD)()
                result_downloaded = client.send_torrent(result)
            else:
                logger.log(u"Torrent file content is empty", logger.WARNING)
                result_downloaded = False
    else:
        logger.log(u"Unknown result type, unable to download it (%r)" % result.resultType, logger.ERROR)
        result_downloaded = False

    if not result_downloaded:
        return False

    if app.USE_FAILED_DOWNLOADS:
        failed_history.log_snatch(result)

    ui.notifications.message('Episode snatched', result.name)

    history.log_snatch(result)

    # don't notify when we re-download an episode
    sql_l = []
    trakt_data = []
    for curEpObj in result.episodes:
        with curEpObj.lock:
            if is_first_best_match(result):
                curEpObj.status = Quality.composite_status(SNATCHED_BEST, result.quality)
            else:
                curEpObj.status = Quality.composite_status(end_status, result.quality)
            # Reset all others fields to the "snatched" status
            # New snatch by default doesn't have nfo/tbn
            curEpObj.hasnfo = False
            curEpObj.hastbn = False

            # We can't reset location because we need to know what we are replacing
            # curEpObj.location = ''

            # Size and release name are fetched in PP (only for downloaded status, not snatched)
            curEpObj.file_size = 0
            curEpObj.release_name = ''

            # Need to reset subtitle settings because it's a different file
            curEpObj.subtitles = list()
            curEpObj.subtitles_searchcount = 0
            curEpObj.subtitles_lastsearch = '0001-01-01 00:00:00'

            # Need to store the correct is_proper. Not use the old one
            curEpObj.is_proper = True if result.proper_tags else False
            curEpObj.version = 0

            # Release group is parsed in PP
            curEpObj.release_group = ''

            curEpObj.manually_searched = result.manually_searched

            sql_l.append(curEpObj.get_sql())

        if curEpObj.status not in Quality.DOWNLOADED:
            notify_message = curEpObj.formatted_filename('%SN - %Sx%0E - %EN - %QN')
            if all([app.SEEDERS_LEECHERS_IN_NOTIFY, result.seeders not in (-1, None),
                    result.leechers not in (-1, None)]):
                notifiers.notify_snatch("{0} with {1} seeders and {2} leechers from {3}".format
                                        (notify_message, result.seeders,
                                         result.leechers, result.provider.name), is_proper)
            else:
                notifiers.notify_snatch("{0} from {1}".format(notify_message, result.provider.name), is_proper)

            if app.USE_TRAKT and app.TRAKT_SYNC_WATCHLIST:
                trakt_data.append((curEpObj.season, curEpObj.episode))
                logger.log(u'Adding {0} {1} to Trakt watchlist'.format
                           (result.show.name, episode_num(curEpObj.season, curEpObj.episode)), logger.INFO)

    if trakt_data:
        data_episode = notifiers.trakt_notifier.trakt_episode_data_generate(trakt_data)
        if data_episode:
            notifiers.trakt_notifier.update_watchlist(result.show, data_episode=data_episode, update="add")

    if sql_l:
        main_db_con = db.DBConnection()
        main_db_con.mass_action(sql_l)

    return True