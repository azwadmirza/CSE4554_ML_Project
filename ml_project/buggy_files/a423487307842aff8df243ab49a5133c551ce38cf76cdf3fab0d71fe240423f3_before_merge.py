def initialize(consoleLogging=True):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    with INIT_LOCK:
        # pylint: disable=global-statement
        global BRANCH, GIT_RESET, GIT_REMOTE, GIT_REMOTE_URL, CUR_COMMIT_HASH, CUR_COMMIT_BRANCH, ACTUAL_LOG_DIR, LOG_DIR, LOG_NR, LOG_SIZE, WEB_PORT, WEB_LOG, ENCRYPTION_VERSION, ENCRYPTION_SECRET, WEB_ROOT, WEB_USERNAME, WEB_PASSWORD, WEB_HOST, WEB_IPV6, WEB_COOKIE_SECRET, WEB_USE_GZIP, API_KEY, ENABLE_HTTPS, HTTPS_CERT, HTTPS_KEY, \
            HANDLE_REVERSE_PROXY, USE_NZBS, USE_TORRENTS, NZB_METHOD, NZB_DIR, DOWNLOAD_PROPERS, RANDOMIZE_PROVIDERS, CHECK_PROPERS_INTERVAL, ALLOW_HIGH_PRIORITY, SAB_FORCED, TORRENT_METHOD, NOTIFY_ON_LOGIN, \
            SAB_USERNAME, SAB_PASSWORD, SAB_APIKEY, SAB_CATEGORY, SAB_CATEGORY_BACKLOG, SAB_CATEGORY_ANIME, SAB_CATEGORY_ANIME_BACKLOG, SAB_HOST, \
            NZBGET_USERNAME, NZBGET_PASSWORD, NZBGET_CATEGORY, NZBGET_CATEGORY_BACKLOG, NZBGET_CATEGORY_ANIME, NZBGET_CATEGORY_ANIME_BACKLOG, NZBGET_PRIORITY, NZBGET_HOST, NZBGET_USE_HTTPS, backlogSearchScheduler, \
            TORRENT_USERNAME, TORRENT_PASSWORD, TORRENT_HOST, TORRENT_PATH, TORRENT_SEED_TIME, TORRENT_PAUSED, TORRENT_HIGH_BANDWIDTH, TORRENT_LABEL, TORRENT_LABEL_ANIME, TORRENT_VERIFY_CERT, TORRENT_RPCURL, TORRENT_AUTH_TYPE, \
            USE_KODI, KODI_ALWAYS_ON, KODI_NOTIFY_ONSNATCH, KODI_NOTIFY_ONDOWNLOAD, KODI_NOTIFY_ONSUBTITLEDOWNLOAD, KODI_UPDATE_FULL, KODI_UPDATE_ONLYFIRST, \
            KODI_UPDATE_LIBRARY, KODI_HOST, KODI_USERNAME, KODI_PASSWORD, BACKLOG_FREQUENCY, \
            USE_TRAKT, TRAKT_USERNAME, TRAKT_ACCESS_TOKEN, TRAKT_REFRESH_TOKEN, TRAKT_REMOVE_WATCHLIST, TRAKT_SYNC_WATCHLIST, TRAKT_REMOVE_SHOW_FROM_SICKRAGE, TRAKT_METHOD_ADD, TRAKT_START_PAUSED, traktCheckerScheduler, TRAKT_USE_RECOMMENDED, TRAKT_SYNC, TRAKT_SYNC_REMOVE, TRAKT_DEFAULT_INDEXER, TRAKT_REMOVE_SERIESLIST, TRAKT_TIMEOUT, TRAKT_BLACKLIST_NAME, \
            USE_PLEX_SERVER, PLEX_NOTIFY_ONSNATCH, PLEX_NOTIFY_ONDOWNLOAD, PLEX_NOTIFY_ONSUBTITLEDOWNLOAD, PLEX_UPDATE_LIBRARY, USE_PLEX_CLIENT, PLEX_CLIENT_USERNAME, PLEX_CLIENT_PASSWORD, \
            PLEX_SERVER_HOST, PLEX_SERVER_TOKEN, PLEX_CLIENT_HOST, PLEX_SERVER_USERNAME, PLEX_SERVER_PASSWORD, PLEX_SERVER_HTTPS, MIN_BACKLOG_FREQUENCY, SKIP_REMOVED_FILES, ALLOWED_EXTENSIONS, \
            USE_EMBY, EMBY_HOST, EMBY_APIKEY, SITE_MESSAGES, \
            showUpdateScheduler, INDEXER_DEFAULT_LANGUAGE, EP_DEFAULT_DELETED_STATUS, LAUNCH_BROWSER, TRASH_REMOVE_SHOW, TRASH_ROTATE_LOGS, SORT_ARTICLE, \
            NEWZNAB_DATA, NZBS, NZBS_UID, NZBS_HASH, INDEXER_DEFAULT, INDEXER_TIMEOUT, USENET_RETENTION, TORRENT_DIR, \
            QUALITY_DEFAULT, SEASON_FOLDERS_DEFAULT, SUBTITLES_DEFAULT, STATUS_DEFAULT, STATUS_DEFAULT_AFTER, \
            GROWL_NOTIFY_ONSNATCH, GROWL_NOTIFY_ONDOWNLOAD, GROWL_NOTIFY_ONSUBTITLEDOWNLOAD, TWITTER_NOTIFY_ONSNATCH, TWITTER_NOTIFY_ONDOWNLOAD, TWITTER_NOTIFY_ONSUBTITLEDOWNLOAD, USE_FREEMOBILE, FREEMOBILE_ID, FREEMOBILE_APIKEY, FREEMOBILE_NOTIFY_ONSNATCH, FREEMOBILE_NOTIFY_ONDOWNLOAD, FREEMOBILE_NOTIFY_ONSUBTITLEDOWNLOAD, \
            USE_TELEGRAM, TELEGRAM_ID, TELEGRAM_APIKEY, TELEGRAM_NOTIFY_ONSNATCH, TELEGRAM_NOTIFY_ONDOWNLOAD, TELEGRAM_NOTIFY_ONSUBTITLEDOWNLOAD, \
            USE_JOIN, JOIN_ID, JOIN_NOTIFY_ONSNATCH, JOIN_NOTIFY_ONDOWNLOAD, JOIN_NOTIFY_ONSUBTITLEDOWNLOAD, \
            USE_GROWL, GROWL_HOST, GROWL_PASSWORD, USE_PROWL, PROWL_NOTIFY_ONSNATCH, PROWL_NOTIFY_ONDOWNLOAD, PROWL_NOTIFY_ONSUBTITLEDOWNLOAD, PROWL_API, PROWL_PRIORITY, PROWL_MESSAGE_TITLE, \
            USE_PYTIVO, PYTIVO_NOTIFY_ONSNATCH, PYTIVO_NOTIFY_ONDOWNLOAD, PYTIVO_NOTIFY_ONSUBTITLEDOWNLOAD, PYTIVO_UPDATE_LIBRARY, PYTIVO_HOST, PYTIVO_SHARE_NAME, PYTIVO_TIVO_NAME, \
            USE_NMA, NMA_NOTIFY_ONSNATCH, NMA_NOTIFY_ONDOWNLOAD, NMA_NOTIFY_ONSUBTITLEDOWNLOAD, NMA_API, NMA_PRIORITY, \
            USE_PUSHALOT, PUSHALOT_NOTIFY_ONSNATCH, PUSHALOT_NOTIFY_ONDOWNLOAD, PUSHALOT_NOTIFY_ONSUBTITLEDOWNLOAD, PUSHALOT_AUTHORIZATIONTOKEN, \
            USE_PUSHBULLET, PUSHBULLET_NOTIFY_ONSNATCH, PUSHBULLET_NOTIFY_ONDOWNLOAD, PUSHBULLET_NOTIFY_ONSUBTITLEDOWNLOAD, PUSHBULLET_API, PUSHBULLET_DEVICE, PUSHBULLET_CHANNEL,\
            versionCheckScheduler, VERSION_NOTIFY, AUTO_UPDATE, NOTIFY_ON_UPDATE, PROCESS_AUTOMATICALLY, NO_DELETE, USE_ICACLS, UNPACK, CPU_PRESET, \
            UNPACK_DIR, UNRAR_TOOL, ALT_UNRAR_TOOL, KEEP_PROCESSED_DIR, PROCESS_METHOD, PROCESSOR_FOLLOW_SYMLINKS, DELRARCONTENTS, TV_DOWNLOAD_DIR, UPDATE_FREQUENCY, \
            showQueueScheduler, searchQueueScheduler, postProcessorTaskScheduler, ROOT_DIRS, CACHE_DIR, ACTUAL_CACHE_DIR, TIMEZONE_DISPLAY, \
            NAMING_PATTERN, NAMING_MULTI_EP, NAMING_ANIME_MULTI_EP, NAMING_FORCE_FOLDERS, NAMING_ABD_PATTERN, NAMING_CUSTOM_ABD, NAMING_SPORTS_PATTERN, NAMING_CUSTOM_SPORTS, NAMING_ANIME_PATTERN, NAMING_CUSTOM_ANIME, NAMING_STRIP_YEAR, \
            RENAME_EPISODES, AIRDATE_EPISODES, FILE_TIMESTAMP_TIMEZONE, properFinderScheduler, PROVIDER_ORDER, autoPostProcessorScheduler, \
            providerList, newznabProviderList, torrentRssProviderList, \
            EXTRA_SCRIPTS, USE_TWITTER, TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_PREFIX, DAILYSEARCH_FREQUENCY, TWITTER_DMTO, TWITTER_USEDM, \
            USE_TWILIO, TWILIO_NOTIFY_ONSNATCH, TWILIO_NOTIFY_ONDOWNLOAD, TWILIO_NOTIFY_ONSUBTITLEDOWNLOAD, TWILIO_PHONE_SID, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_TO_NUMBER, \
            USE_BOXCAR2, BOXCAR2_ACCESSTOKEN, BOXCAR2_NOTIFY_ONDOWNLOAD, BOXCAR2_NOTIFY_ONSUBTITLEDOWNLOAD, BOXCAR2_NOTIFY_ONSNATCH, \
            USE_PUSHOVER, PUSHOVER_USERKEY, PUSHOVER_APIKEY, PUSHOVER_DEVICE, PUSHOVER_NOTIFY_ONDOWNLOAD, PUSHOVER_NOTIFY_ONSUBTITLEDOWNLOAD, PUSHOVER_NOTIFY_ONSNATCH, PUSHOVER_SOUND, PUSHOVER_PRIORITY, \
            USE_LIBNOTIFY, LIBNOTIFY_NOTIFY_ONSNATCH, LIBNOTIFY_NOTIFY_ONDOWNLOAD, LIBNOTIFY_NOTIFY_ONSUBTITLEDOWNLOAD, USE_NMJ, NMJ_HOST, NMJ_DATABASE, NMJ_MOUNT, USE_NMJv2, NMJv2_HOST, NMJv2_DATABASE, NMJv2_DBLOC, USE_SYNOINDEX, \
            USE_SYNOLOGYNOTIFIER, SYNOLOGYNOTIFIER_NOTIFY_ONSNATCH, SYNOLOGYNOTIFIER_NOTIFY_ONDOWNLOAD, SYNOLOGYNOTIFIER_NOTIFY_ONSUBTITLEDOWNLOAD, \
            USE_EMAIL, EMAIL_HOST, EMAIL_PORT, EMAIL_TLS, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_NOTIFY_ONSNATCH, EMAIL_NOTIFY_ONDOWNLOAD, EMAIL_NOTIFY_ONSUBTITLEDOWNLOAD, EMAIL_LIST, EMAIL_SUBJECT, \
            USE_LISTVIEW, METADATA_KODI, METADATA_KODI_12PLUS, METADATA_MEDIABROWSER, METADATA_PS3, metadata_provider_dict, \
            NEWZBIN, NEWZBIN_USERNAME, NEWZBIN_PASSWORD, GIT_PATH, MOVE_ASSOCIATED_FILES, DELETE_NON_ASSOCIATED_FILES, SYNC_FILES, POSTPONE_IF_SYNC_FILES, dailySearchScheduler, NFO_RENAME, \
            GUI_NAME, HOME_LAYOUT, HISTORY_LAYOUT, DISPLAY_SHOW_SPECIALS, COMING_EPS_LAYOUT, COMING_EPS_SORT, COMING_EPS_DISPLAY_PAUSED, COMING_EPS_MISSED_RANGE, FUZZY_DATING, TRIM_ZERO, DATE_PRESET, TIME_PRESET, TIME_PRESET_W_SECONDS, THEME_NAME, \
            POSTER_SORTBY, POSTER_SORTDIR, HISTORY_LIMIT, CREATE_MISSING_SHOW_DIRS, ADD_SHOWS_WO_DIR, USE_FREE_SPACE_CHECK, \
            METADATA_WDTV, METADATA_TIVO, METADATA_MEDE8ER, IGNORE_WORDS, TRACKERS_LIST, IGNORED_SUBS_LIST, REQUIRE_WORDS, CALENDAR_UNPROTECTED, CALENDAR_ICONS, NO_RESTART, \
            USE_SUBTITLES, SUBTITLES_INCLUDE_SPECIALS, SUBTITLES_LANGUAGES, SUBTITLES_DIR, SUBTITLES_SERVICES_LIST, SUBTITLES_SERVICES_ENABLED, SUBTITLES_HISTORY, SUBTITLES_FINDER_FREQUENCY, SUBTITLES_MULTI, SUBTITLES_KEEP_ONLY_WANTED, EMBEDDED_SUBTITLES_ALL, SUBTITLES_EXTRA_SCRIPTS, SUBTITLES_PERFECT_MATCH, subtitlesFinderScheduler, \
            SUBTITLES_HEARING_IMPAIRED, ADDIC7ED_USER, ADDIC7ED_PASS, ITASA_USER, ITASA_PASS, LEGENDASTV_USER, LEGENDASTV_PASS, OPENSUBTITLES_USER, OPENSUBTITLES_PASS, \
            USE_FAILED_DOWNLOADS, DELETE_FAILED, ANON_REDIRECT, LOCALHOST_IP, DEBUG, DBDEBUG, DEFAULT_PAGE, PROXY_SETTING, PROXY_INDEXERS, \
            AUTOPOSTPROCESSOR_FREQUENCY, SHOWUPDATE_HOUR, \
            ANIME_DEFAULT, NAMING_ANIME, ANIMESUPPORT, USE_ANIDB, ANIDB_USERNAME, ANIDB_PASSWORD, ANIDB_USE_MYLIST, \
            ANIME_SPLIT_HOME, ANIME_SPLIT_HOME_IN_TABS, SCENE_DEFAULT, DOWNLOAD_URL, BACKLOG_DAYS, GIT_AUTH_TYPE, GIT_USERNAME, GIT_PASSWORD, GIT_TOKEN, \
            DEVELOPER, DISPLAY_ALL_SEASONS, SSL_VERIFY, NEWS_LAST_READ, NEWS_LATEST, SOCKET_TIMEOUT, \
            SYNOLOGY_DSM_HOST, SYNOLOGY_DSM_USERNAME, SYNOLOGY_DSM_PASSWORD, SYNOLOGY_DSM_PATH, GUI_LANG, SICKRAGE_BACKGROUND, SICKRAGE_BACKGROUND_PATH, \
            FANART_BACKGROUND, FANART_BACKGROUND_OPACITY, USE_SLACK, SLACK_NOTIFY_SNATCH, SLACK_NOTIFY_DOWNLOAD, SLACK_WEBHOOK, \
            USE_DISCORD, DISCORD_NOTIFY_SNATCH, DISCORD_NOTIFY_DOWNLOAD, DISCORD_WEBHOOK

        if __INITIALIZED__:
            return False

        check_section(CFG, 'General')
        check_section(CFG, 'Blackhole')
        check_section(CFG, 'Newzbin')
        check_section(CFG, 'SABnzbd')
        check_section(CFG, 'NZBget')
        check_section(CFG, 'KODI')
        check_section(CFG, 'PLEX')
        check_section(CFG, 'Emby')
        check_section(CFG, 'Growl')
        check_section(CFG, 'Prowl')
        check_section(CFG, 'Twitter')
        check_section(CFG, 'Boxcar2')
        check_section(CFG, 'NMJ')
        check_section(CFG, 'NMJv2')
        check_section(CFG, 'Synology')
        check_section(CFG, 'SynologyNotifier')
        check_section(CFG, 'pyTivo')
        check_section(CFG, 'NMA')
        check_section(CFG, 'Pushalot')
        check_section(CFG, 'Pushbullet')
        check_section(CFG, 'Subtitles')
        check_section(CFG, 'pyTivo')
        check_section(CFG, 'Slack')
        check_section(CFG, 'Discord')

        # Need to be before any passwords
        ENCRYPTION_VERSION = check_setting_int(CFG, 'General', 'encryption_version')
        ENCRYPTION_SECRET = check_setting_str(CFG, 'General', 'encryption_secret', helpers.generateCookieSecret(), censor_log=True)

        # git login info
        GIT_AUTH_TYPE = check_setting_int(CFG, 'General', 'git_auth_type')
        GIT_USERNAME = check_setting_str(CFG, 'General', 'git_username')
        GIT_PASSWORD = check_setting_str(CFG, 'General', 'git_password', censor_log=True)
        GIT_TOKEN = check_setting_str(CFG, 'General', 'git_token_password', censor_log=True) # encryption needed
        DEVELOPER = check_setting_bool(CFG, 'General', 'developer')

        # debugging
        DEBUG = check_setting_bool(CFG, 'General', 'debug')
        DBDEBUG = check_setting_bool(CFG, 'General', 'dbdebug')

        DEFAULT_PAGE = check_setting_str(CFG, 'General', 'default_page', 'home')
        if DEFAULT_PAGE not in ('home', 'schedule', 'history', 'news', 'IRC'):
            DEFAULT_PAGE = 'home'

        ACTUAL_LOG_DIR = check_setting_str(CFG, 'General', 'log_dir', 'Logs')
        LOG_DIR = ek(os.path.normpath, ek(os.path.join, DATA_DIR, ACTUAL_LOG_DIR))
        LOG_NR = check_setting_int(CFG, 'General', 'log_nr', 5)  # Default to 5 backup file (sickrage.log.x)
        LOG_SIZE = check_setting_float(CFG, 'General', 'log_size', 10.0)  # Default to max 10MB per logfile

        if LOG_SIZE > 100:
            LOG_SIZE = 10.0
        fileLogging = True

        if not helpers.makeDir(LOG_DIR):
            sys.stderr.write("!!! No log folder, logging to screen only!\n")
            fileLogging = False

        # init logging
        logger.init_logging(console_logging=consoleLogging, file_logging=fileLogging, debug_logging=DEBUG, database_logging=DBDEBUG)

        # Initializes sickbeard.gh
        setup_github()

        # git reset on update
        GIT_RESET = check_setting_bool(CFG, 'General', 'git_reset', True)

        # current git branch
        BRANCH = check_setting_str(CFG, 'General', 'branch')

        # git_remote
        GIT_REMOTE = check_setting_str(CFG, 'General', 'git_remote', 'origin')
        GIT_REMOTE_URL = check_setting_str(CFG, 'General', 'git_remote_url',
                                           'https://github.com/{0}/{1}.git'.format(GIT_ORG, GIT_REPO))

        if 'sickragetv' in GIT_REMOTE_URL.lower():
            GIT_REMOTE_URL = 'https://github.com/SickRage/SickRage.git'

        # current commit hash
        CUR_COMMIT_HASH = check_setting_str(CFG, 'General', 'cur_commit_hash')

        # current commit branch
        CUR_COMMIT_BRANCH = check_setting_str(CFG, 'General', 'cur_commit_branch')

        ACTUAL_CACHE_DIR = check_setting_str(CFG, 'General', 'cache_dir', 'cache')

        # fix bad configs due to buggy code
        if ACTUAL_CACHE_DIR == 'None':
            ACTUAL_CACHE_DIR = 'cache'

        # unless they specify, put the cache dir inside the data dir
        if not ek(os.path.isabs, ACTUAL_CACHE_DIR):
            CACHE_DIR = ek(os.path.join, DATA_DIR, ACTUAL_CACHE_DIR)
        else:
            CACHE_DIR = ACTUAL_CACHE_DIR

        if not helpers.makeDir(CACHE_DIR):
            logger.log("!!! Creating local cache dir failed, using system default", logger.ERROR)
            CACHE_DIR = None

        # Check if we need to perform a restore of the cache folder
        try:
            restoreDir = ek(os.path.join, DATA_DIR, 'restore')
            if ek(os.path.exists, restoreDir) and ek(os.path.exists, ek(os.path.join, restoreDir, 'cache')):
                def restoreCache(srcDir, dstDir):
                    def path_leaf(path):
                        head, tail = ek(os.path.split, path)
                        return tail or ek(os.path.basename, head)

                    try:
                        if ek(os.path.isdir, dstDir):
                            bakFilename = '{0}-{1}'.format(path_leaf(dstDir), datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S'))
                            shutil.move(dstDir, ek(os.path.join, ek(os.path.dirname, dstDir), bakFilename))

                        shutil.move(srcDir, dstDir)
                        logger.log("Restore: restoring cache successful", logger.INFO)
                    except Exception as e:
                        logger.log("Restore: restoring cache failed: {0}".format(e), logger.ERROR)

                restoreCache(ek(os.path.join, restoreDir, 'cache'), CACHE_DIR)
        except Exception as e:
            logger.log("Restore: restoring cache failed: {0}".format(ex(e)), logger.ERROR)
        finally:
            if ek(os.path.exists, ek(os.path.join, DATA_DIR, 'restore')):
                try:
                    shutil.rmtree(ek(os.path.join, DATA_DIR, 'restore'))
                except Exception as e:
                    logger.log("Restore: Unable to remove the restore directory: {0}".format(ex(e)), logger.ERROR)

                for cleanupDir in ['mako', 'sessions', 'indexers', 'rss']:
                    try:
                        shutil.rmtree(ek(os.path.join, CACHE_DIR, cleanupDir))
                    except Exception as e:
                        if cleanupDir not in ['rss', 'sessions', 'indexers']:
                            logger.log("Restore: Unable to remove the cache/{0} directory: {1}".format(cleanupDir, ex(e)), logger.WARNING)

        THEME_NAME = check_setting_str(CFG, 'GUI', 'theme_name', 'dark')
        SICKRAGE_BACKGROUND = check_setting_bool(CFG, 'GUI', 'sickrage_background')
        SICKRAGE_BACKGROUND_PATH = check_setting_str(CFG, 'GUI', 'sickrage_background_path')
        FANART_BACKGROUND = check_setting_bool(CFG, 'GUI', 'fanart_background', True)
        FANART_BACKGROUND_OPACITY = check_setting_float(CFG, 'GUI', 'fanart_background_opacity', 0.4)

        GUI_NAME = check_setting_str(CFG, 'GUI', 'gui_name', 'slick')
        GUI_LANG = check_setting_str(CFG, 'GUI', 'language')

        if GUI_LANG:
            gettext.translation('messages', LOCALE_DIR, languages=[GUI_LANG], codeset='UTF-8').install(unicode=1)
        else:
            gettext.install('messages', LOCALE_DIR, unicode=1, codeset='UTF-8')

        load_gettext_translations(LOCALE_DIR, 'messages')

        SOCKET_TIMEOUT = check_setting_int(CFG, 'General', 'socket_timeout', 30)
        socket.setdefaulttimeout(SOCKET_TIMEOUT)

        try:
            WEB_PORT = check_setting_int(CFG, 'General', 'web_port', 8081)
        except Exception:
            WEB_PORT = 8081

        if 21 > WEB_PORT > 65535:
            WEB_PORT = 8081

        WEB_HOST = check_setting_str(CFG, 'General', 'web_host', '0.0.0.0')
        WEB_IPV6 = check_setting_bool(CFG, 'General', 'web_ipv6')
        WEB_ROOT = check_setting_str(CFG, 'General', 'web_root').rstrip("/")
        WEB_LOG = check_setting_bool(CFG, 'General', 'web_log')
        WEB_USERNAME = check_setting_str(CFG, 'General', 'web_username', censor_log=True)
        WEB_PASSWORD = check_setting_str(CFG, 'General', 'web_password', censor_log=True)
        WEB_COOKIE_SECRET = check_setting_str(CFG, 'General', 'web_cookie_secret', helpers.generateCookieSecret(), censor_log=True)
        if not WEB_COOKIE_SECRET:
            WEB_COOKIE_SECRET = helpers.generateCookieSecret()

        WEB_USE_GZIP = check_setting_bool(CFG, 'General', 'web_use_gzip', True)

        SSL_VERIFY = check_setting_bool(CFG, 'General', 'ssl_verify', True)

        INDEXER_DEFAULT_LANGUAGE = check_setting_str(CFG, 'General', 'indexerDefaultLang', 'en')
        EP_DEFAULT_DELETED_STATUS = check_setting_int(CFG, 'General', 'ep_default_deleted_status', 6)

        LAUNCH_BROWSER = check_setting_bool(CFG, 'General', 'launch_browser', True)

        DOWNLOAD_URL = check_setting_str(CFG, 'General', 'download_url')

        LOCALHOST_IP = check_setting_str(CFG, 'General', 'localhost_ip')

        CPU_PRESET = check_setting_str(CFG, 'General', 'cpu_preset', 'NORMAL')

        ANON_REDIRECT = check_setting_str(CFG, 'General', 'anon_redirect', 'http://dereferer.org/?')
        PROXY_SETTING = check_setting_str(CFG, 'General', 'proxy_setting')
        PROXY_INDEXERS = check_setting_int(CFG, 'General', 'proxy_indexers', 1)

        # attempt to help prevent users from breaking links by using a bad url
        if not ANON_REDIRECT.endswith('?'):
            ANON_REDIRECT = ''

        TRASH_REMOVE_SHOW = check_setting_bool(CFG, 'General', 'trash_remove_show')
        TRASH_ROTATE_LOGS = check_setting_bool(CFG, 'General', 'trash_rotate_logs')

        SORT_ARTICLE = check_setting_bool(CFG, 'General', 'sort_article')

        API_KEY = check_setting_str(CFG, 'General', 'api_key', censor_log=True)

        ENABLE_HTTPS = check_setting_bool(CFG, 'General', 'enable_https')

        NOTIFY_ON_LOGIN = check_setting_bool(CFG, 'General', 'notify_on_login')

        HTTPS_CERT = check_setting_str(CFG, 'General', 'https_cert', 'server.crt')
        HTTPS_KEY = check_setting_str(CFG, 'General', 'https_key', 'server.key')

        HANDLE_REVERSE_PROXY = check_setting_bool(CFG, 'General', 'handle_reverse_proxy')

        ROOT_DIRS = check_setting_str(CFG, 'General', 'root_dirs')
        if not re.match(r'\d+\|[^|]+(?:\|[^|]+)*', ROOT_DIRS):
            ROOT_DIRS = ''

        QUALITY_DEFAULT = check_setting_int(CFG, 'General', 'quality_default', SD)
        STATUS_DEFAULT = check_setting_int(CFG, 'General', 'status_default', SKIPPED)
        STATUS_DEFAULT_AFTER = check_setting_int(CFG, 'General', 'status_default_after', WANTED)
        VERSION_NOTIFY = check_setting_bool(CFG, 'General', 'version_notify', True)
        AUTO_UPDATE = check_setting_bool(CFG, 'General', 'auto_update')
        NOTIFY_ON_UPDATE = check_setting_bool(CFG, 'General', 'notify_on_update', True)
        SEASON_FOLDERS_DEFAULT = check_setting_bool(CFG, 'General', 'season_folders_default', True)
        INDEXER_DEFAULT = check_setting_int(CFG, 'General', 'indexer_default')
        INDEXER_TIMEOUT = check_setting_int(CFG, 'General', 'indexer_timeout', 20)
        ANIME_DEFAULT = check_setting_bool(CFG, 'General', 'anime_default')
        SCENE_DEFAULT = check_setting_bool(CFG, 'General', 'scene_default')

        PROVIDER_ORDER = check_setting_str(CFG, 'General', 'provider_order').split()

        NAMING_PATTERN = check_setting_str(CFG, 'General', 'naming_pattern', 'Season %0S/%SN - S%0SE%0E - %EN')
        NAMING_ABD_PATTERN = check_setting_str(CFG, 'General', 'naming_abd_pattern', '%SN - %A.D - %EN')
        NAMING_CUSTOM_ABD = check_setting_bool(CFG, 'General', 'naming_custom_abd')
        NAMING_SPORTS_PATTERN = check_setting_str(CFG, 'General', 'naming_sports_pattern', '%SN - %A-D - %EN')
        NAMING_ANIME_PATTERN = check_setting_str(CFG, 'General', 'naming_anime_pattern',
                                                 'Season %0S/%SN - S%0SE%0E - %EN')
        NAMING_ANIME = check_setting_int(CFG, 'General', 'naming_anime', 3)
        NAMING_CUSTOM_SPORTS = check_setting_bool(CFG, 'General', 'naming_custom_sports')
        NAMING_CUSTOM_ANIME = check_setting_bool(CFG, 'General', 'naming_custom_anime')
        NAMING_MULTI_EP = check_setting_int(CFG, 'General', 'naming_multi_ep', 1)
        NAMING_ANIME_MULTI_EP = check_setting_int(CFG, 'General', 'naming_anime_multi_ep', 1)
        NAMING_FORCE_FOLDERS = naming.check_force_season_folders()
        NAMING_STRIP_YEAR = check_setting_bool(CFG, 'General', 'naming_strip_year')

        USE_NZBS = check_setting_bool(CFG, 'General', 'use_nzbs')
        USE_TORRENTS = check_setting_bool(CFG, 'General', 'use_torrents', True)

        NZB_METHOD = check_setting_str(CFG, 'General', 'nzb_method', 'blackhole')
        if NZB_METHOD not in ('blackhole', 'sabnzbd', 'nzbget', 'download_station'):
            NZB_METHOD = 'blackhole'

        TORRENT_METHOD = check_setting_str(CFG, 'General', 'torrent_method', 'blackhole')
        if TORRENT_METHOD not in ('blackhole', 'utorrent', 'transmission', 'deluge', 'deluged', 'download_station', 'rtorrent', 'qbittorrent', 'mlnet', 'putio'):
            TORRENT_METHOD = 'blackhole'

        DOWNLOAD_PROPERS = check_setting_bool(CFG, 'General', 'download_propers', True)
        CHECK_PROPERS_INTERVAL = check_setting_str(CFG, 'General', 'check_propers_interval')
        if CHECK_PROPERS_INTERVAL not in ('15m', '45m', '90m', '4h', 'daily'):
            CHECK_PROPERS_INTERVAL = 'daily'

        RANDOMIZE_PROVIDERS = check_setting_bool(CFG, 'General', 'randomize_providers')

        ALLOW_HIGH_PRIORITY = check_setting_bool(CFG, 'General', 'allow_high_priority', True)

        SKIP_REMOVED_FILES = check_setting_bool(CFG, 'General', 'skip_removed_files')

        ALLOWED_EXTENSIONS = check_setting_str(CFG, 'General', 'allowed_extensions', ALLOWED_EXTENSIONS)

        USENET_RETENTION = check_setting_int(CFG, 'General', 'usenet_retention', 500)

        AUTOPOSTPROCESSOR_FREQUENCY = check_setting_int(CFG, 'General', 'autopostprocessor_frequency',
                                                        DEFAULT_AUTOPOSTPROCESSOR_FREQUENCY)
        if AUTOPOSTPROCESSOR_FREQUENCY < MIN_AUTOPOSTPROCESSOR_FREQUENCY:
            AUTOPOSTPROCESSOR_FREQUENCY = MIN_AUTOPOSTPROCESSOR_FREQUENCY

        DAILYSEARCH_FREQUENCY = check_setting_int(CFG, 'General', 'dailysearch_frequency',
                                                  DEFAULT_DAILYSEARCH_FREQUENCY)
        if DAILYSEARCH_FREQUENCY < MIN_DAILYSEARCH_FREQUENCY:
            DAILYSEARCH_FREQUENCY = MIN_DAILYSEARCH_FREQUENCY

        MIN_BACKLOG_FREQUENCY = get_backlog_cycle_time()
        BACKLOG_FREQUENCY = check_setting_int(CFG, 'General', 'backlog_frequency', DEFAULT_BACKLOG_FREQUENCY)
        if BACKLOG_FREQUENCY < MIN_BACKLOG_FREQUENCY:
            BACKLOG_FREQUENCY = MIN_BACKLOG_FREQUENCY

        UPDATE_FREQUENCY = check_setting_int(CFG, 'General', 'update_frequency', DEFAULT_UPDATE_FREQUENCY)
        if UPDATE_FREQUENCY < MIN_UPDATE_FREQUENCY:
            UPDATE_FREQUENCY = MIN_UPDATE_FREQUENCY

        SHOWUPDATE_HOUR = check_setting_int(CFG, 'General', 'showupdate_hour', DEFAULT_SHOWUPDATE_HOUR)
        if SHOWUPDATE_HOUR > 23:
            SHOWUPDATE_HOUR = 0
        elif SHOWUPDATE_HOUR < 0:
            SHOWUPDATE_HOUR = 0

        BACKLOG_DAYS = check_setting_int(CFG, 'General', 'backlog_days', 7)

        NEWS_LAST_READ = check_setting_str(CFG, 'General', 'news_last_read', '1970-01-01')
        NEWS_LATEST = NEWS_LAST_READ

        NZB_DIR = check_setting_str(CFG, 'Blackhole', 'nzb_dir')
        TORRENT_DIR = check_setting_str(CFG, 'Blackhole', 'torrent_dir')

        TV_DOWNLOAD_DIR = check_setting_str(CFG, 'General', 'tv_download_dir')
        PROCESS_AUTOMATICALLY = check_setting_bool(CFG, 'General', 'process_automatically')
        NO_DELETE = check_setting_bool(CFG, 'General', 'no_delete')
        USE_ICACLS = check_setting_bool(CFG, 'General', 'use_icacls', True)
        UNPACK = check_setting_int(CFG, 'General', 'unpack')
        UNPACK_DIR = check_setting_str(CFG, 'General', 'unpack_dir')

        config.change_unrar_tool(
            check_setting_str(CFG, 'General', 'unrar_tool', rarfile.UNRAR_TOOL),
            check_setting_str(CFG, 'General', 'alt_unrar_tool', rarfile.ALT_TOOL)
        )

        RENAME_EPISODES = check_setting_bool(CFG, 'General', 'rename_episodes', True)
        AIRDATE_EPISODES = check_setting_bool(CFG, 'General', 'airdate_episodes')
        FILE_TIMESTAMP_TIMEZONE = check_setting_str(CFG, 'General', 'file_timestamp_timezone', 'network')
        KEEP_PROCESSED_DIR = check_setting_bool(CFG, 'General', 'keep_processed_dir', True)
        PROCESS_METHOD = check_setting_str(CFG, 'General', 'process_method', 'copy' if KEEP_PROCESSED_DIR else 'move')
        PROCESSOR_FOLLOW_SYMLINKS = check_setting_bool(CFG, 'General', 'processor_follow_symlinks')
        DELRARCONTENTS = check_setting_bool(CFG, 'General', 'del_rar_contents')
        MOVE_ASSOCIATED_FILES = check_setting_bool(CFG, 'General', 'move_associated_files')
        DELETE_NON_ASSOCIATED_FILES = check_setting_bool(CFG, 'General', 'delete_non_associated_files', True)
        POSTPONE_IF_SYNC_FILES = check_setting_bool(CFG, 'General', 'postpone_if_sync_files', True)
        SYNC_FILES = check_setting_str(CFG, 'General', 'sync_files', SYNC_FILES)
        NFO_RENAME = check_setting_bool(CFG, 'General', 'nfo_rename', True)
        CREATE_MISSING_SHOW_DIRS = check_setting_bool(CFG, 'General', 'create_missing_show_dirs')
        ADD_SHOWS_WO_DIR = check_setting_bool(CFG, 'General', 'add_shows_wo_dir')
        USE_FREE_SPACE_CHECK = check_setting_bool(CFG, 'General', 'use_free_space_check', True)

        NZBS = check_setting_bool(CFG, 'NZBs', 'nzbs')
        NZBS_UID = check_setting_str(CFG, 'NZBs', 'nzbs_uid', censor_log=True)
        NZBS_HASH = check_setting_str(CFG, 'NZBs', 'nzbs_hash', censor_log=True)

        NEWZBIN = check_setting_bool(CFG, 'Newzbin', 'newzbin')
        NEWZBIN_USERNAME = check_setting_str(CFG, 'Newzbin', 'newzbin_username', censor_log=True)
        NEWZBIN_PASSWORD = check_setting_str(CFG, 'Newzbin', 'newzbin_password', censor_log=True)

        SAB_USERNAME = check_setting_str(CFG, 'SABnzbd', 'sab_username', censor_log=True)
        SAB_PASSWORD = check_setting_str(CFG, 'SABnzbd', 'sab_password', censor_log=True)
        SAB_APIKEY = check_setting_str(CFG, 'SABnzbd', 'sab_apikey', censor_log=True)
        SAB_CATEGORY = check_setting_str(CFG, 'SABnzbd', 'sab_category', 'tv')
        SAB_CATEGORY_BACKLOG = check_setting_str(CFG, 'SABnzbd', 'sab_category_backlog', SAB_CATEGORY)
        SAB_CATEGORY_ANIME = check_setting_str(CFG, 'SABnzbd', 'sab_category_anime', 'anime')
        SAB_CATEGORY_ANIME_BACKLOG = check_setting_str(CFG, 'SABnzbd', 'sab_category_anime_backlog', SAB_CATEGORY_ANIME)
        SAB_HOST = check_setting_str(CFG, 'SABnzbd', 'sab_host')
        SAB_FORCED = check_setting_bool(CFG, 'SABnzbd', 'sab_forced')

        NZBGET_USERNAME = check_setting_str(CFG, 'NZBget', 'nzbget_username', 'nzbget', censor_log=True)
        NZBGET_PASSWORD = check_setting_str(CFG, 'NZBget', 'nzbget_password', 'tegbzn6789', censor_log=True)
        NZBGET_CATEGORY = check_setting_str(CFG, 'NZBget', 'nzbget_category', 'tv')
        NZBGET_CATEGORY_BACKLOG = check_setting_str(CFG, 'NZBget', 'nzbget_category_backlog', NZBGET_CATEGORY)
        NZBGET_CATEGORY_ANIME = check_setting_str(CFG, 'NZBget', 'nzbget_category_anime', 'anime')
        NZBGET_CATEGORY_ANIME_BACKLOG = check_setting_str(CFG, 'NZBget', 'nzbget_category_anime_backlog', NZBGET_CATEGORY_ANIME)
        NZBGET_HOST = check_setting_str(CFG, 'NZBget', 'nzbget_host')
        NZBGET_USE_HTTPS = check_setting_bool(CFG, 'NZBget', 'nzbget_use_https')
        NZBGET_PRIORITY = check_setting_int(CFG, 'NZBget', 'nzbget_priority', 100)

        TORRENT_USERNAME = check_setting_str(CFG, 'TORRENT', 'torrent_username', censor_log=True)
        TORRENT_PASSWORD = check_setting_str(CFG, 'TORRENT', 'torrent_password', censor_log=True)
        TORRENT_HOST = check_setting_str(CFG, 'TORRENT', 'torrent_host')
        TORRENT_PATH = check_setting_str(CFG, 'TORRENT', 'torrent_path')
        TORRENT_SEED_TIME = check_setting_int(CFG, 'TORRENT', 'torrent_seed_time')
        TORRENT_PAUSED = check_setting_bool(CFG, 'TORRENT', 'torrent_paused')
        TORRENT_HIGH_BANDWIDTH = check_setting_bool(CFG, 'TORRENT', 'torrent_high_bandwidth')
        TORRENT_LABEL = check_setting_str(CFG, 'TORRENT', 'torrent_label')
        TORRENT_LABEL_ANIME = check_setting_str(CFG, 'TORRENT', 'torrent_label_anime')
        TORRENT_VERIFY_CERT = check_setting_bool(CFG, 'TORRENT', 'torrent_verify_cert')
        TORRENT_RPCURL = check_setting_str(CFG, 'TORRENT', 'torrent_rpcurl', 'transmission')
        TORRENT_AUTH_TYPE = check_setting_str(CFG, 'TORRENT', 'torrent_auth_type')

        SYNOLOGY_DSM_HOST = check_setting_str(CFG, 'Synology', 'host')
        SYNOLOGY_DSM_USERNAME = check_setting_str(CFG, 'Synology', 'username', censor_log=True)
        SYNOLOGY_DSM_PASSWORD = check_setting_str(CFG, 'Synology', 'password', censor_log=True)
        SYNOLOGY_DSM_PATH = check_setting_str(CFG, 'Synology', 'path')

        USE_KODI = check_setting_bool(CFG, 'KODI', 'use_kodi')
        KODI_ALWAYS_ON = check_setting_bool(CFG, 'KODI', 'kodi_always_on', True)
        KODI_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'KODI', 'kodi_notify_onsnatch')
        KODI_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'KODI', 'kodi_notify_ondownload')
        KODI_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'KODI', 'kodi_notify_onsubtitledownload')
        KODI_UPDATE_LIBRARY = check_setting_bool(CFG, 'KODI', 'kodi_update_library')
        KODI_UPDATE_FULL = check_setting_bool(CFG, 'KODI', 'kodi_update_full')
        KODI_UPDATE_ONLYFIRST = check_setting_bool(CFG, 'KODI', 'kodi_update_onlyfirst')
        KODI_HOST = check_setting_str(CFG, 'KODI', 'kodi_host')
        KODI_USERNAME = check_setting_str(CFG, 'KODI', 'kodi_username', censor_log=True)
        KODI_PASSWORD = check_setting_str(CFG, 'KODI', 'kodi_password', censor_log=True)

        USE_PLEX_SERVER = check_setting_bool(CFG, 'Plex', 'use_plex_server')
        PLEX_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Plex', 'plex_notify_onsnatch')
        PLEX_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Plex', 'plex_notify_ondownload')
        PLEX_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Plex', 'plex_notify_onsubtitledownload')
        PLEX_UPDATE_LIBRARY = check_setting_bool(CFG, 'Plex', 'plex_update_library')
        PLEX_SERVER_HOST = check_setting_str(CFG, 'Plex', 'plex_server_host')
        PLEX_SERVER_TOKEN = check_setting_str(CFG, 'Plex', 'plex_server_token')
        PLEX_CLIENT_HOST = check_setting_str(CFG, 'Plex', 'plex_client_host')
        PLEX_SERVER_USERNAME = check_setting_str(CFG, 'Plex', 'plex_server_username', censor_log=True)
        PLEX_SERVER_PASSWORD = check_setting_str(CFG, 'Plex', 'plex_server_password', censor_log=True)
        USE_PLEX_CLIENT = check_setting_bool(CFG, 'Plex', 'use_plex_client')
        PLEX_CLIENT_USERNAME = check_setting_str(CFG, 'Plex', 'plex_client_username', censor_log=True)
        PLEX_CLIENT_PASSWORD = check_setting_str(CFG, 'Plex', 'plex_client_password', censor_log=True)
        PLEX_SERVER_HTTPS = check_setting_bool(CFG, 'Plex', 'plex_server_https')

        USE_EMBY = check_setting_bool(CFG, 'Emby', 'use_emby')
        EMBY_HOST = check_setting_str(CFG, 'Emby', 'emby_host')
        EMBY_APIKEY = check_setting_str(CFG, 'Emby', 'emby_apikey')

        USE_GROWL = check_setting_bool(CFG, 'Growl', 'use_growl')
        GROWL_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Growl', 'growl_notify_onsnatch')
        GROWL_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Growl', 'growl_notify_ondownload')
        GROWL_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Growl', 'growl_notify_onsubtitledownload')
        GROWL_HOST = check_setting_str(CFG, 'Growl', 'growl_host')
        GROWL_PASSWORD = check_setting_str(CFG, 'Growl', 'growl_password', censor_log=True)

        USE_FREEMOBILE = check_setting_bool(CFG, 'FreeMobile', 'use_freemobile')
        FREEMOBILE_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'FreeMobile', 'freemobile_notify_onsnatch')
        FREEMOBILE_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'FreeMobile', 'freemobile_notify_ondownload')
        FREEMOBILE_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'FreeMobile', 'freemobile_notify_onsubtitledownload')
        FREEMOBILE_ID = check_setting_str(CFG, 'FreeMobile', 'freemobile_id')
        FREEMOBILE_APIKEY = check_setting_str(CFG, 'FreeMobile', 'freemobile_apikey')

        USE_TELEGRAM = check_setting_bool(CFG, 'Telegram', 'use_telegram')
        TELEGRAM_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Telegram', 'telegram_notify_onsnatch')
        TELEGRAM_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Telegram', 'telegram_notify_ondownload')
        TELEGRAM_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Telegram', 'telegram_notify_onsubtitledownload')
        TELEGRAM_ID = check_setting_str(CFG, 'Telegram', 'telegram_id')
        TELEGRAM_APIKEY = check_setting_str(CFG, 'Telegram', 'telegram_apikey')

        USE_JOIN = check_setting_bool(CFG, 'Join', 'use_join')
        JOIN_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Join', 'join_notify_onsnatch')
        JOIN_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Join', 'join_notify_ondownload')
        JOIN_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Join', 'join_notify_onsubtitledownload')
        JOIN_ID = check_setting_str(CFG, 'Join', 'join_id')

        USE_PROWL = check_setting_bool(CFG, 'Prowl', 'use_prowl')
        PROWL_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Prowl', 'prowl_notify_onsnatch')
        PROWL_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Prowl', 'prowl_notify_ondownload')
        PROWL_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Prowl', 'prowl_notify_onsubtitledownload')
        PROWL_API = check_setting_str(CFG, 'Prowl', 'prowl_api', censor_log=True)
        PROWL_PRIORITY = check_setting_str(CFG, 'Prowl', 'prowl_priority', "0")
        PROWL_MESSAGE_TITLE = check_setting_str(CFG, 'Prowl', 'prowl_message_title', "SickRage")

        USE_TWITTER = check_setting_bool(CFG, 'Twitter', 'use_twitter')
        TWITTER_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Twitter', 'twitter_notify_onsnatch')
        TWITTER_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Twitter', 'twitter_notify_ondownload')
        TWITTER_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Twitter', 'twitter_notify_onsubtitledownload')
        TWITTER_USERNAME = check_setting_str(CFG, 'Twitter', 'twitter_username', censor_log=True)
        TWITTER_PASSWORD = check_setting_str(CFG, 'Twitter', 'twitter_password', censor_log=True)
        TWITTER_PREFIX = check_setting_str(CFG, 'Twitter', 'twitter_prefix', GIT_REPO)
        TWITTER_DMTO = check_setting_str(CFG, 'Twitter', 'twitter_dmto')
        TWITTER_USEDM = check_setting_bool(CFG, 'Twitter', 'twitter_usedm')

        USE_TWILIO = check_setting_bool(CFG, 'Twilio', 'use_twilio')
        TWILIO_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Twilio', 'twilio_notify_onsnatch')
        TWILIO_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Twilio', 'twilio_notify_ondownload')
        TWILIO_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Twilio', 'twilio_notify_onsubtitledownload')
        TWILIO_PHONE_SID = check_setting_str(CFG, 'Twilio', 'twilio_phone_sid', censor_log=True)
        TWILIO_ACCOUNT_SID = check_setting_str(CFG, 'Twilio', 'twilio_account_sid', censor_log=True)
        TWILIO_AUTH_TOKEN = check_setting_str(CFG, 'Twilio', 'twilio_auth_token', censor_log=True)
        TWILIO_TO_NUMBER = check_setting_str(CFG, 'Twilio', 'twilio_to_number', censor_log=True)

        USE_BOXCAR2 = check_setting_bool(CFG, 'Boxcar2', 'use_boxcar2')
        BOXCAR2_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Boxcar2', 'boxcar2_notify_onsnatch')
        BOXCAR2_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Boxcar2', 'boxcar2_notify_ondownload')
        BOXCAR2_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Boxcar2', 'boxcar2_notify_onsubtitledownload')
        BOXCAR2_ACCESSTOKEN = check_setting_str(CFG, 'Boxcar2', 'boxcar2_accesstoken', censor_log=True)

        USE_PUSHOVER = check_setting_bool(CFG, 'Pushover', 'use_pushover')
        PUSHOVER_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Pushover', 'pushover_notify_onsnatch')
        PUSHOVER_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Pushover', 'pushover_notify_ondownload')
        PUSHOVER_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Pushover', 'pushover_notify_onsubtitledownload')
        PUSHOVER_USERKEY = check_setting_str(CFG, 'Pushover', 'pushover_userkey', censor_log=True)
        PUSHOVER_APIKEY = check_setting_str(CFG, 'Pushover', 'pushover_apikey', censor_log=True)
        PUSHOVER_DEVICE = check_setting_str(CFG, 'Pushover', 'pushover_device')
        PUSHOVER_SOUND = check_setting_str(CFG, 'Pushover', 'pushover_sound', 'pushover')
        PUSHOVER_PRIORITY = check_setting_str(CFG, 'Pushover', 'pushover_priority', "0")

        USE_LIBNOTIFY = check_setting_bool(CFG, 'Libnotify', 'use_libnotify')
        LIBNOTIFY_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Libnotify', 'libnotify_notify_onsnatch')
        LIBNOTIFY_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Libnotify', 'libnotify_notify_ondownload')
        LIBNOTIFY_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Libnotify', 'libnotify_notify_onsubtitledownload')

        USE_NMJ = check_setting_bool(CFG, 'NMJ', 'use_nmj')
        NMJ_HOST = check_setting_str(CFG, 'NMJ', 'nmj_host')
        NMJ_DATABASE = check_setting_str(CFG, 'NMJ', 'nmj_database')
        NMJ_MOUNT = check_setting_str(CFG, 'NMJ', 'nmj_mount')

        USE_NMJv2 = check_setting_bool(CFG, 'NMJv2', 'use_nmjv2')
        NMJv2_HOST = check_setting_str(CFG, 'NMJv2', 'nmjv2_host')
        NMJv2_DATABASE = check_setting_str(CFG, 'NMJv2', 'nmjv2_database')
        NMJv2_DBLOC = check_setting_str(CFG, 'NMJv2', 'nmjv2_dbloc')

        USE_SYNOINDEX = check_setting_bool(CFG, 'Synology', 'use_synoindex')

        USE_SYNOLOGYNOTIFIER = check_setting_bool(CFG, 'SynologyNotifier', 'use_synologynotifier')
        SYNOLOGYNOTIFIER_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'SynologyNotifier', 'synologynotifier_notify_onsnatch')
        SYNOLOGYNOTIFIER_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'SynologyNotifier', 'synologynotifier_notify_ondownload')
        SYNOLOGYNOTIFIER_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'SynologyNotifier', 'synologynotifier_notify_onsubtitledownload')

        USE_SLACK = check_setting_bool(CFG, 'Slack', 'use_slack')
        SLACK_NOTIFY_SNATCH = check_setting_bool(CFG, 'Slack', 'slack_notify_snatch')
        SLACK_NOTIFY_DOWNLOAD = check_setting_bool(CFG, 'Slack', 'slack_notify_download')
        SLACK_WEBHOOK = check_setting_str(CFG, 'Slack', 'slack_webhook')

        USE_DISCORD = check_setting_bool(CFG, 'Discord', 'use_discord')
        DISCORD_NOTIFY_SNATCH = check_setting_bool(CFG, 'Discord', 'discord_notify_snatch')
        DISCORD_NOTIFY_DOWNLOAD = check_setting_bool(CFG, 'Discord', 'discord_notify_download')
        DISCORD_WEBHOOK = check_setting_str(CFG, 'Discord', 'discord_webhook')

        USE_TRAKT = check_setting_bool(CFG, 'Trakt', 'use_trakt')
        TRAKT_USERNAME = check_setting_str(CFG, 'Trakt', 'trakt_username', censor_log=True)
        TRAKT_ACCESS_TOKEN = check_setting_str(CFG, 'Trakt', 'trakt_access_token', censor_log=True)
        TRAKT_REFRESH_TOKEN = check_setting_str(CFG, 'Trakt', 'trakt_refresh_token', censor_log=True)
        TRAKT_REMOVE_WATCHLIST = check_setting_bool(CFG, 'Trakt', 'trakt_remove_watchlist')
        TRAKT_REMOVE_SERIESLIST = check_setting_bool(CFG, 'Trakt', 'trakt_remove_serieslist')
        TRAKT_REMOVE_SHOW_FROM_SICKRAGE = check_setting_bool(CFG, 'Trakt', 'trakt_remove_show_from_sickrage')
        TRAKT_SYNC_WATCHLIST = check_setting_bool(CFG, 'Trakt', 'trakt_sync_watchlist')
        TRAKT_METHOD_ADD = check_setting_int(CFG, 'Trakt', 'trakt_method_add')
        TRAKT_START_PAUSED = check_setting_bool(CFG, 'Trakt', 'trakt_start_paused')
        TRAKT_USE_RECOMMENDED = check_setting_bool(CFG, 'Trakt', 'trakt_use_recommended')
        TRAKT_SYNC = check_setting_bool(CFG, 'Trakt', 'trakt_sync')
        TRAKT_SYNC_REMOVE = check_setting_bool(CFG, 'Trakt', 'trakt_sync_remove')
        TRAKT_DEFAULT_INDEXER = check_setting_int(CFG, 'Trakt', 'trakt_default_indexer', 1)
        TRAKT_TIMEOUT = check_setting_int(CFG, 'Trakt', 'trakt_timeout', 30)
        TRAKT_BLACKLIST_NAME = check_setting_str(CFG, 'Trakt', 'trakt_blacklist_name')

        USE_PYTIVO = check_setting_bool(CFG, 'pyTivo', 'use_pytivo')
        PYTIVO_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'pyTivo', 'pytivo_notify_onsnatch')
        PYTIVO_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'pyTivo', 'pytivo_notify_ondownload')
        PYTIVO_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'pyTivo', 'pytivo_notify_onsubtitledownload')
        PYTIVO_UPDATE_LIBRARY = check_setting_bool(CFG, 'pyTivo', 'pyTivo_update_library')
        PYTIVO_HOST = check_setting_str(CFG, 'pyTivo', 'pytivo_host')
        PYTIVO_SHARE_NAME = check_setting_str(CFG, 'pyTivo', 'pytivo_share_name')
        PYTIVO_TIVO_NAME = check_setting_str(CFG, 'pyTivo', 'pytivo_tivo_name')

        USE_NMA = check_setting_bool(CFG, 'NMA', 'use_nma')
        NMA_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'NMA', 'nma_notify_onsnatch')
        NMA_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'NMA', 'nma_notify_ondownload')
        NMA_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'NMA', 'nma_notify_onsubtitledownload')
        NMA_API = check_setting_str(CFG, 'NMA', 'nma_api', censor_log=True)
        NMA_PRIORITY = check_setting_str(CFG, 'NMA', 'nma_priority', "0")

        USE_PUSHALOT = check_setting_bool(CFG, 'Pushalot', 'use_pushalot')
        PUSHALOT_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Pushalot', 'pushalot_notify_onsnatch')
        PUSHALOT_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Pushalot', 'pushalot_notify_ondownload')
        PUSHALOT_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Pushalot', 'pushalot_notify_onsubtitledownload')
        PUSHALOT_AUTHORIZATIONTOKEN = check_setting_str(CFG, 'Pushalot', 'pushalot_authorizationtoken', censor_log=True)

        USE_PUSHBULLET = check_setting_bool(CFG, 'Pushbullet', 'use_pushbullet')
        PUSHBULLET_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Pushbullet', 'pushbullet_notify_onsnatch')
        PUSHBULLET_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Pushbullet', 'pushbullet_notify_ondownload')
        PUSHBULLET_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Pushbullet', 'pushbullet_notify_onsubtitledownload')
        PUSHBULLET_API = check_setting_str(CFG, 'Pushbullet', 'pushbullet_api', censor_log=True)
        PUSHBULLET_DEVICE = check_setting_str(CFG, 'Pushbullet', 'pushbullet_device')
        PUSHBULLET_CHANNEL = check_setting_str(CFG, 'Pushbullet', 'pushbullet_channel')

        USE_EMAIL = check_setting_bool(CFG, 'Email', 'use_email')
        EMAIL_NOTIFY_ONSNATCH = check_setting_bool(CFG, 'Email', 'email_notify_onsnatch')
        EMAIL_NOTIFY_ONDOWNLOAD = check_setting_bool(CFG, 'Email', 'email_notify_ondownload')
        EMAIL_NOTIFY_ONSUBTITLEDOWNLOAD = check_setting_bool(CFG, 'Email', 'email_notify_onsubtitledownload')
        EMAIL_HOST = check_setting_str(CFG, 'Email', 'email_host')
        EMAIL_PORT = check_setting_int(CFG, 'Email', 'email_port', 25)
        EMAIL_TLS = check_setting_bool(CFG, 'Email', 'email_tls')
        EMAIL_USER = check_setting_str(CFG, 'Email', 'email_user', censor_log=True)
        EMAIL_PASSWORD = check_setting_str(CFG, 'Email', 'email_password', censor_log=True)
        EMAIL_FROM = check_setting_str(CFG, 'Email', 'email_from')
        EMAIL_LIST = check_setting_str(CFG, 'Email', 'email_list')
        EMAIL_SUBJECT = check_setting_str(CFG, 'Email', 'email_subject')

        USE_SUBTITLES = check_setting_bool(CFG, 'Subtitles', 'use_subtitles')
        SUBTITLES_INCLUDE_SPECIALS = check_setting_bool(CFG, 'Subtitles', 'subtitles_include_specials', True)
        SUBTITLES_LANGUAGES = check_setting_str(CFG, 'Subtitles', 'subtitles_languages').split(',')
        if SUBTITLES_LANGUAGES[0] == '':
            SUBTITLES_LANGUAGES = []
        SUBTITLES_DIR = check_setting_str(CFG, 'Subtitles', 'subtitles_dir')
        SUBTITLES_SERVICES_LIST = check_setting_str(CFG, 'Subtitles', 'SUBTITLES_SERVICES_LIST').split(',')
        SUBTITLES_SERVICES_ENABLED = [int(x) for x in
                                      check_setting_str(CFG, 'Subtitles', 'SUBTITLES_SERVICES_ENABLED').split('|')
                                      if x]
        SUBTITLES_DEFAULT = check_setting_bool(CFG, 'Subtitles', 'subtitles_default')
        SUBTITLES_HISTORY = check_setting_bool(CFG, 'Subtitles', 'subtitles_history')
        SUBTITLES_PERFECT_MATCH = check_setting_bool(CFG, 'Subtitles', 'subtitles_perfect_match', True)
        EMBEDDED_SUBTITLES_ALL = check_setting_bool(CFG, 'Subtitles', 'embedded_subtitles_all')
        SUBTITLES_HEARING_IMPAIRED = check_setting_bool(CFG, 'Subtitles', 'subtitles_hearing_impaired')
        SUBTITLES_FINDER_FREQUENCY = check_setting_int(CFG, 'Subtitles', 'subtitles_finder_frequency', 1)
        SUBTITLES_MULTI = check_setting_bool(CFG, 'Subtitles', 'subtitles_multi', True)
        SUBTITLES_KEEP_ONLY_WANTED = check_setting_bool(CFG, 'Subtitles', 'subtitles_keep_only_wanted')
        SUBTITLES_EXTRA_SCRIPTS = [x.strip() for x in check_setting_str(CFG, 'Subtitles', 'subtitles_extra_scripts').split('|') if x.strip()]

        ADDIC7ED_USER = check_setting_str(CFG, 'Subtitles', 'addic7ed_username', censor_log=True)
        ADDIC7ED_PASS = check_setting_str(CFG, 'Subtitles', 'addic7ed_password', censor_log=True)

        ITASA_USER = check_setting_str(CFG, 'Subtitles', 'itasa_username', censor_log=True)
        ITASA_PASS = check_setting_str(CFG, 'Subtitles', 'itasa_password', censor_log=True)

        LEGENDASTV_USER = check_setting_str(CFG, 'Subtitles', 'legendastv_username', censor_log=True)
        LEGENDASTV_PASS = check_setting_str(CFG, 'Subtitles', 'legendastv_password', censor_log=True)

        OPENSUBTITLES_USER = check_setting_str(CFG, 'Subtitles', 'opensubtitles_username', censor_log=True)
        OPENSUBTITLES_PASS = check_setting_str(CFG, 'Subtitles', 'opensubtitles_password', censor_log=True)

        USE_FAILED_DOWNLOADS = check_setting_bool(CFG, 'FailedDownloads', 'use_failed_downloads')
        DELETE_FAILED = check_setting_bool(CFG, 'FailedDownloads', 'delete_failed')

        GIT_PATH = check_setting_str(CFG, 'General', 'git_path')

        IGNORE_WORDS = check_setting_str(CFG, 'General', 'ignore_words', IGNORE_WORDS)
        TRACKERS_LIST = check_setting_str(CFG, 'General', 'trackers_list', TRACKERS_LIST)
        REQUIRE_WORDS = check_setting_str(CFG, 'General', 'require_words', REQUIRE_WORDS)
        IGNORED_SUBS_LIST = check_setting_str(CFG, 'General', 'ignored_subs_list', IGNORED_SUBS_LIST)

        CALENDAR_UNPROTECTED = check_setting_bool(CFG, 'General', 'calendar_unprotected')
        CALENDAR_ICONS = check_setting_bool(CFG, 'General', 'calendar_icons')

        NO_RESTART = check_setting_bool(CFG, 'General', 'no_restart')

        EXTRA_SCRIPTS = [x.strip() for x in check_setting_str(CFG, 'General', 'extra_scripts').split('|') if x.strip()]

        USE_LISTVIEW = check_setting_bool(CFG, 'General', 'use_listview')

        ANIMESUPPORT = False
        USE_ANIDB = check_setting_bool(CFG, 'ANIDB', 'use_anidb')
        ANIDB_USERNAME = check_setting_str(CFG, 'ANIDB', 'anidb_username', censor_log=True)
        ANIDB_PASSWORD = check_setting_str(CFG, 'ANIDB', 'anidb_password', censor_log=True)
        ANIDB_USE_MYLIST = check_setting_bool(CFG, 'ANIDB', 'anidb_use_mylist')

        ANIME_SPLIT_HOME = check_setting_bool(CFG, 'ANIME', 'anime_split_home')
        ANIME_SPLIT_HOME_IN_TABS = check_setting_bool(CFG, 'ANIME', 'anime_split_home_in_tabs')

        METADATA_KODI = check_setting_str(CFG, 'General', 'metadata_kodi', '0|0|0|0|0|0|0|0|0|0')
        METADATA_KODI_12PLUS = check_setting_str(CFG, 'General', 'metadata_kodi_12plus', '0|0|0|0|0|0|0|0|0|0')
        METADATA_MEDIABROWSER = check_setting_str(CFG, 'General', 'metadata_mediabrowser', '0|0|0|0|0|0|0|0|0|0')
        METADATA_PS3 = check_setting_str(CFG, 'General', 'metadata_ps3', '0|0|0|0|0|0|0|0|0|0')
        METADATA_WDTV = check_setting_str(CFG, 'General', 'metadata_wdtv', '0|0|0|0|0|0|0|0|0|0')
        METADATA_TIVO = check_setting_str(CFG, 'General', 'metadata_tivo', '0|0|0|0|0|0|0|0|0|0')
        METADATA_MEDE8ER = check_setting_str(CFG, 'General', 'metadata_mede8er', '0|0|0|0|0|0|0|0|0|0')

        HOME_LAYOUT = check_setting_str(CFG, 'GUI', 'home_layout', 'poster')
        HISTORY_LAYOUT = check_setting_str(CFG, 'GUI', 'history_layout', 'detailed')
        HISTORY_LIMIT = check_setting_str(CFG, 'GUI', 'history_limit', '100')
        DISPLAY_SHOW_SPECIALS = check_setting_bool(CFG, 'GUI', 'display_show_specials', True)
        COMING_EPS_LAYOUT = check_setting_str(CFG, 'GUI', 'coming_eps_layout', 'banner')
        COMING_EPS_DISPLAY_PAUSED = check_setting_bool(CFG, 'GUI', 'coming_eps_display_paused')
        COMING_EPS_SORT = check_setting_str(CFG, 'GUI', 'coming_eps_sort', 'date')
        COMING_EPS_MISSED_RANGE = check_setting_int(CFG, 'GUI', 'coming_eps_missed_range', 7)
        FUZZY_DATING = check_setting_bool(CFG, 'GUI', 'fuzzy_dating')
        TRIM_ZERO = check_setting_bool(CFG, 'GUI', 'trim_zero')
        DATE_PRESET = check_setting_str(CFG, 'GUI', 'date_preset', '%x')
        TIME_PRESET_W_SECONDS = check_setting_str(CFG, 'GUI', 'time_preset', '%I:%M:%S %p')
        TIME_PRESET = TIME_PRESET_W_SECONDS.replace(":%S", "")
        TIMEZONE_DISPLAY = check_setting_str(CFG, 'GUI', 'timezone_display', 'local')
        POSTER_SORTBY = check_setting_str(CFG, 'GUI', 'poster_sortby', 'name')
        POSTER_SORTDIR = check_setting_int(CFG, 'GUI', 'poster_sortdir', 1)
        DISPLAY_ALL_SEASONS = check_setting_bool(CFG, 'General', 'display_all_seasons', True)

        # initialize NZB and TORRENT providers
        providerList = providers.makeProviderList()

        NEWZNAB_DATA = check_setting_str(CFG, 'Newznab', 'newznab_data')
        newznabProviderList = NewznabProvider.get_providers_list(NEWZNAB_DATA)

        TORRENTRSS_DATA = check_setting_str(CFG, 'TorrentRss', 'torrentrss_data')
        torrentRssProviderList = TorrentRssProvider.get_providers_list(TORRENTRSS_DATA)

        # dynamically load provider settings
        for curTorrentProvider in [curProvider for curProvider in providers.sortedProviderList() if
                                   curProvider.provider_type == GenericProvider.TORRENT]:
            curTorrentProvider.enabled = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id())
            if hasattr(curTorrentProvider, 'custom_url'):
                curTorrentProvider.custom_url = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                                  curTorrentProvider.get_id() + '_custom_url',
                                                                  '', censor_log=True)
            if hasattr(curTorrentProvider, 'api_key'):
                curTorrentProvider.api_key = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_api_key', censor_log=True)
            if hasattr(curTorrentProvider, 'hash'):
                curTorrentProvider.hash = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                            curTorrentProvider.get_id() + '_hash', censor_log=True)
            if hasattr(curTorrentProvider, 'digest'):
                curTorrentProvider.digest = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                              curTorrentProvider.get_id() + '_digest', censor_log=True)
            if hasattr(curTorrentProvider, 'username'):
                curTorrentProvider.username = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                                curTorrentProvider.get_id() + '_username', censor_log=True)
            if hasattr(curTorrentProvider, 'password'):
                curTorrentProvider.password = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                                curTorrentProvider.get_id() + '_password', censor_log=True)
            if hasattr(curTorrentProvider, 'passkey'):
                curTorrentProvider.passkey = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_passkey', censor_log=True)
            if hasattr(curTorrentProvider, 'pin'):
                curTorrentProvider.pin = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                           curTorrentProvider.get_id() + '_pin', censor_log=True)
            if hasattr(curTorrentProvider, 'confirmed'):
                curTorrentProvider.confirmed = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_confirmed', True)

            if hasattr(curTorrentProvider, 'ranked'):
                curTorrentProvider.ranked = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_ranked', True)

            if hasattr(curTorrentProvider, 'engrelease'):
                curTorrentProvider.engrelease = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_engrelease')

            if hasattr(curTorrentProvider, 'onlyspasearch'):
                curTorrentProvider.onlyspasearch = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_onlyspasearch')

            if hasattr(curTorrentProvider, 'sorting'):
                curTorrentProvider.sorting = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_sorting', 'seeders')
            if hasattr(curTorrentProvider, 'options'):
                curTorrentProvider.options = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_options', '')
            if hasattr(curTorrentProvider, 'ratio'):
                curTorrentProvider.ratio = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                             curTorrentProvider.get_id() + '_ratio', '')
            if hasattr(curTorrentProvider, 'minseed'):
                curTorrentProvider.minseed = check_setting_int(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_minseed', 1)
            if hasattr(curTorrentProvider, 'minleech'):
                curTorrentProvider.minleech = check_setting_int(CFG, curTorrentProvider.get_id().upper(),
                                                                curTorrentProvider.get_id() + '_minleech', 0)
            if hasattr(curTorrentProvider, 'freeleech'):
                curTorrentProvider.freeleech = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_freeleech')
            if hasattr(curTorrentProvider, 'search_mode'):
                curTorrentProvider.search_mode = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                                   curTorrentProvider.get_id() + '_search_mode',
                                                                   'eponly')
            if hasattr(curTorrentProvider, 'search_fallback'):
                curTorrentProvider.search_fallback = check_setting_bool(CFG, curTorrentProvider.get_id().upper(),
                                                                            curTorrentProvider.get_id() + '_search_fallback')

            if hasattr(curTorrentProvider, 'enable_daily'):
                curTorrentProvider.enable_daily = check_setting_bool(CFG, curTorrentProvider.get_id().upper(),
                                                                         curTorrentProvider.get_id() + '_enable_daily', True)

            if hasattr(curTorrentProvider, 'enable_backlog'):
                curTorrentProvider.enable_backlog = check_setting_bool(CFG, curTorrentProvider.get_id().upper(),
                                                                           curTorrentProvider.get_id() + '_enable_backlog',
                                                                           curTorrentProvider.supports_backlog)

            if hasattr(curTorrentProvider, 'cat'):
                curTorrentProvider.cat = check_setting_int(CFG, curTorrentProvider.get_id().upper(),
                                                           curTorrentProvider.get_id() + '_cat', 0)
            if hasattr(curTorrentProvider, 'subtitle'):
                curTorrentProvider.subtitle = check_setting_bool(CFG, curTorrentProvider.get_id().upper(), curTorrentProvider.get_id() + '_subtitle')

            if hasattr(curTorrentProvider, 'cookies'):
                curTorrentProvider.cookies = check_setting_str(CFG, curTorrentProvider.get_id().upper(),
                                                               curTorrentProvider.get_id() + '_cookies', censor_log=True)

        for curNzbProvider in [curProvider for curProvider in providers.sortedProviderList() if
                               curProvider.provider_type == GenericProvider.NZB]:
            curNzbProvider.enabled = check_setting_bool(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id())

            if hasattr(curNzbProvider, 'api_key'):
                curNzbProvider.api_key = check_setting_str(CFG, curNzbProvider.get_id().upper(),
                                                           curNzbProvider.get_id() + '_api_key', censor_log=True)

            if hasattr(curNzbProvider, 'username'):
                curNzbProvider.username = check_setting_str(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id() + '_username', censor_log=True)
            if hasattr(curNzbProvider, 'search_mode'):
                curNzbProvider.search_mode = check_setting_str(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id() + '_search_mode', 'eponly')

            if hasattr(curNzbProvider, 'search_fallback'):
                curNzbProvider.search_fallback = check_setting_bool(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id() + '_search_fallback')

            if hasattr(curNzbProvider, 'enable_daily'):
                curNzbProvider.enable_daily = check_setting_bool(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id() + '_enable_daily', True)

            if hasattr(curNzbProvider, 'enable_backlog'):
                curNzbProvider.enable_backlog = check_setting_bool(CFG, curNzbProvider.get_id().upper(), curNzbProvider.get_id() + '_enable_backlog',
                                                                  curNzbProvider.supports_backlog)

        providers.check_enabled_providers()

        if not ek(os.path.isfile, CONFIG_FILE):
            logger.log("Unable to find '" + CONFIG_FILE + "', all settings will be default!", logger.DEBUG)
            save_config()

        # initialize the main SB database
        main_db_con = db.DBConnection()
        db.upgradeDatabase(main_db_con, mainDB.InitialSchema)

        # initialize the cache database
        cache_db_con = db.DBConnection('cache.db')
        db.upgradeDatabase(cache_db_con, cache_db.InitialSchema)

        # initialize the failed downloads database
        failed_db_con = db.DBConnection('failed.db')
        db.upgradeDatabase(failed_db_con, failed_db.InitialSchema)

        # fix up any db problems
        main_db_con = db.DBConnection()
        db.sanityCheckDatabase(main_db_con, mainDB.MainSanityCheck)

        # migrate the config if it needs it
        migrator = ConfigMigrator(CFG)
        migrator.migrate_config()

        # initialize metadata_providers
        metadata_provider_dict = metadata.get_metadata_generator_dict()
        for cur_metadata_tuple in [(METADATA_KODI, metadata.kodi),
                                   (METADATA_KODI_12PLUS, metadata.kodi_12plus),
                                   (METADATA_MEDIABROWSER, metadata.mediabrowser),
                                   (METADATA_PS3, metadata.ps3),
                                   (METADATA_WDTV, metadata.wdtv),
                                   (METADATA_TIVO, metadata.tivo),
                                   (METADATA_MEDE8ER, metadata.mede8er)]:

            (cur_metadata_config, cur_metadata_class) = cur_metadata_tuple
            tmp_provider = cur_metadata_class.metadata_class()
            tmp_provider.set_config(cur_metadata_config)
            metadata_provider_dict[tmp_provider.name] = tmp_provider

        # initialize schedulers
        # updaters
        versionCheckScheduler = scheduler.Scheduler(
            versionChecker.CheckVersion(),
            cycleTime=datetime.timedelta(hours=UPDATE_FREQUENCY),
            threadName="CHECKVERSION",
            silent=False
        )

        showQueueScheduler = scheduler.Scheduler(
            show_queue.ShowQueue(),
            cycleTime=datetime.timedelta(seconds=5),
            threadName="SHOWQUEUE"
        )

        showUpdateScheduler = scheduler.Scheduler(
            showUpdater.ShowUpdater(),
            run_delay=datetime.timedelta(seconds=20),
            cycleTime=datetime.timedelta(hours=1),
            start_time=datetime.time(hour=SHOWUPDATE_HOUR),
            threadName="SHOWUPDATER"
        )

        # searchers
        searchQueueScheduler = scheduler.Scheduler(
            search_queue.SearchQueue(),
            run_delay=datetime.timedelta(seconds=10),
            cycleTime=datetime.timedelta(seconds=5),
            threadName="SEARCHQUEUE"
        )

        dailySearchScheduler = scheduler.Scheduler(
            dailysearcher.DailySearcher(),
            run_delay=datetime.timedelta(minutes=10),
            cycleTime=datetime.timedelta(minutes=DAILYSEARCH_FREQUENCY),
            threadName="DAILYSEARCHER"
        )

        update_interval = datetime.timedelta(minutes=BACKLOG_FREQUENCY)
        backlogSearchScheduler = searchBacklog.BacklogSearchScheduler(
            searchBacklog.BacklogSearcher(),
            cycleTime=update_interval,
            threadName="BACKLOG",
            run_delay=update_interval
        )

        search_intervals = {'15m': 15, '45m': 45, '90m': 90, '4h': 4 * 60, 'daily': 24 * 60}
        if CHECK_PROPERS_INTERVAL in search_intervals:
            update_interval = datetime.timedelta(minutes=search_intervals[CHECK_PROPERS_INTERVAL])
            run_at = None
        else:
            update_interval = datetime.timedelta(hours=1)
            run_at = datetime.time(hour=1)  # 1 AM

        properFinderScheduler = scheduler.Scheduler(
            properFinder.ProperFinder(),
            cycleTime=update_interval,
            threadName="FINDPROPERS",
            start_time=run_at,
            run_delay=update_interval,
            silent=not DOWNLOAD_PROPERS
        )

        # processors
        postProcessorTaskScheduler = scheduler.Scheduler(
            post_processing_queue.ProcessingQueue(),
            run_delay=datetime.timedelta(seconds=5),
            cycleTime=datetime.timedelta(seconds=5),
            threadName="POSTPROCESSOR",
        )

        autoPostProcessorScheduler = scheduler.Scheduler(
            auto_postprocessor.PostProcessor(),
            run_delay=datetime.timedelta(minutes=5),
            cycleTime=datetime.timedelta(minutes=AUTOPOSTPROCESSOR_FREQUENCY),
            threadName="POSTPROCESSOR",
            silent=not PROCESS_AUTOMATICALLY,
        )

        traktCheckerScheduler = scheduler.Scheduler(
            traktChecker.TraktChecker(),
            run_delay=datetime.timedelta(minutes=5),
            cycleTime=datetime.timedelta(hours=1),
            threadName="TRAKTCHECKER",
            silent=not USE_TRAKT
        )

        subtitlesFinderScheduler = scheduler.Scheduler(
            subtitles.SubtitlesFinder(),
            run_delay=datetime.timedelta(minutes=10),
            cycleTime=datetime.timedelta(hours=SUBTITLES_FINDER_FREQUENCY),
            threadName="FINDSUBTITLES",
            silent=not USE_SUBTITLES
        )

        __INITIALIZED__['0'] = True
        return True