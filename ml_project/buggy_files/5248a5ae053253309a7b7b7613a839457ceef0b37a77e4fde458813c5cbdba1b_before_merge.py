    def initialize(self, console_logging=True):
        """Initialize global variables and configuration."""
        with app.INIT_LOCK:
            if app.__INITIALIZED__:
                return False

            sections = [
                'General', 'Blackhole', 'Newzbin', 'SABnzbd', 'NZBget', 'KODI', 'PLEX', 'Emby', 'Growl', 'Prowl', 'Twitter',
                'Boxcar2', 'NMJ', 'NMJv2', 'Synology', 'Slack', 'SynologyNotifier', 'pyTivo', 'Pushalot', 'Pushbullet', 'Join',
                'Subtitles', 'pyTivo',
            ]

            for section in sections:
                CheckSection(app.CFG, section)

            app.PRIVACY_LEVEL = check_setting_str(app.CFG, 'General', 'privacy_level', 'normal')
            # Need to be before any passwords
            app.ENCRYPTION_VERSION = check_setting_int(app.CFG, 'General', 'encryption_version', 0)
            app.ENCRYPTION_SECRET = check_setting_str(app.CFG, 'General', 'encryption_secret', helpers.generate_cookie_secret(), censor_log='low')

            # git login info
            app.GIT_AUTH_TYPE = check_setting_int(app.CFG, 'General', 'git_auth_type', 0)
            app.GIT_USERNAME = check_setting_str(app.CFG, 'General', 'git_username', '')
            app.GIT_PASSWORD = check_setting_str(app.CFG, 'General', 'git_password', '', censor_log='low')
            app.GIT_TOKEN = check_setting_str(app.CFG, 'General', 'git_token', '', censor_log='low', encrypted=True)
            app.DEVELOPER = bool(check_setting_int(app.CFG, 'General', 'developer', 0))
            app.PYTHON_VERSION = check_setting_list(app.CFG, 'General', 'python_version', [], transform=int)

            # debugging
            app.DEBUG = bool(check_setting_int(app.CFG, 'General', 'debug', 0))
            app.DBDEBUG = bool(check_setting_int(app.CFG, 'General', 'dbdebug', 0))

            app.DEFAULT_PAGE = check_setting_str(app.CFG, 'General', 'default_page', 'home', valid_values=('home', 'schedule', 'history', 'news', 'IRC'))
            app.SEEDERS_LEECHERS_IN_NOTIFY = check_setting_int(app.CFG, 'General', 'seeders_leechers_in_notify', 1)
            app.ACTUAL_LOG_DIR = check_setting_str(app.CFG, 'General', 'log_dir', 'Logs')
            app.LOG_DIR = os.path.normpath(os.path.join(app.DATA_DIR, app.ACTUAL_LOG_DIR))
            app.LOG_NR = check_setting_int(app.CFG, 'General', 'log_nr', 5)  # Default to 5 backup file (application.log.x)
            app.LOG_SIZE = min(100, check_setting_float(app.CFG, 'General', 'log_size', 10.0))  # Default to max 10MB per logfile

            if not helpers.make_dir(app.LOG_DIR):
                sys.stderr.write('Unable to create log folder {folder}'.format(folder=app.LOG_DIR))
                sys.exit(7)

            # init logging
            app_logger.backwards_compatibility()
            app_logger.init_logging(console_logging=console_logging)

            # git reset on update
            app.GIT_RESET = bool(check_setting_int(app.CFG, 'General', 'git_reset', 1))
            app.GIT_RESET_BRANCHES = check_setting_list(app.CFG, 'General', 'git_reset_branches', app.GIT_RESET_BRANCHES)
            if not app.GIT_RESET_BRANCHES:
                app.GIT_RESET_BRANCHES = []

            # current git branch
            app.BRANCH = check_setting_str(app.CFG, 'General', 'branch', '')

            # git_remote
            app.GIT_REMOTE = check_setting_str(app.CFG, 'General', 'git_remote', 'origin')
            app.GIT_REMOTE_URL = check_setting_str(app.CFG, 'General', 'git_remote_url', app.APPLICATION_URL)

            if not app.DEVELOPER:
                repo_url_re = re.compile(
                    r'(?P<prefix>(?:git@github\.com:)|(?:https://github\.com/))(?P<org>\w+)/(?P<repo>\w+)\.git')
                m = repo_url_re.match(app.GIT_REMOTE_URL)
                if m:
                    groups = m.groupdict()
                    if groups['org'].lower() != app.GIT_ORG.lower() or groups['repo'].lower() != app.GIT_REPO.lower():
                        app.GIT_REMOTE_URL = groups['prefix'] + app.GIT_ORG + '/' + app.GIT_REPO + '.git'
                else:
                    app.GIT_REMOTE_URL = app.APPLICATION_URL

            # current commit hash
            app.CUR_COMMIT_HASH = check_setting_str(app.CFG, 'General', 'cur_commit_hash', '')

            # current commit branch
            app.CUR_COMMIT_BRANCH = check_setting_str(app.CFG, 'General', 'cur_commit_branch', '')
            app.ACTUAL_CACHE_DIR = check_setting_str(app.CFG, 'General', 'cache_dir', 'cache')

            # fix bad configs due to buggy code
            if app.ACTUAL_CACHE_DIR == 'None':
                app.ACTUAL_CACHE_DIR = 'cache'

            # unless they specify, put the cache dir inside the data dir
            if not os.path.isabs(app.ACTUAL_CACHE_DIR):
                app.CACHE_DIR = os.path.join(app.DATA_DIR, app.ACTUAL_CACHE_DIR)
            else:
                app.CACHE_DIR = app.ACTUAL_CACHE_DIR

            if not helpers.make_dir(app.CACHE_DIR):
                logger.error(u'Creating local cache dir failed, using system default')
                app.CACHE_DIR = None

            app.FANART_BACKGROUND = bool(check_setting_int(app.CFG, 'GUI', 'fanart_background', 1))
            app.FANART_BACKGROUND_OPACITY = check_setting_float(app.CFG, 'GUI', 'fanart_background_opacity', 0.4)

            app.THEME_NAME = check_setting_str(app.CFG, 'GUI', 'theme_name', 'dark',
                                               valid_values=[t.name for t in app.AVAILABLE_THEMES])

            app.SOCKET_TIMEOUT = check_setting_int(app.CFG, 'General', 'socket_timeout', 30)
            socket.setdefaulttimeout(app.SOCKET_TIMEOUT)

            try:
                app.WEB_PORT = check_setting_int(app.CFG, 'General', 'web_port', 8081)
            except Exception:
                app.WEB_PORT = 8081

            if not 21 < app.WEB_PORT < 65535:
                app.WEB_PORT = 8081

            app.WEB_HOST = check_setting_str(app.CFG, 'General', 'web_host', '0.0.0.0')
            app.WEB_IPV6 = bool(check_setting_int(app.CFG, 'General', 'web_ipv6', 0))
            app.WEB_ROOT = check_setting_str(app.CFG, 'General', 'web_root', '').rstrip('/')
            app.WEB_LOG = bool(check_setting_int(app.CFG, 'General', 'web_log', 0))
            app.WEB_USERNAME = check_setting_str(app.CFG, 'General', 'web_username', '', censor_log='normal')
            app.WEB_PASSWORD = check_setting_str(app.CFG, 'General', 'web_password', '', censor_log='low')
            app.WEB_COOKIE_SECRET = check_setting_str(app.CFG, 'General', 'web_cookie_secret', helpers.generate_cookie_secret(), censor_log='low')
            if not app.WEB_COOKIE_SECRET:
                app.WEB_COOKIE_SECRET = helpers.generate_cookie_secret()

            app.WEB_USE_GZIP = bool(check_setting_int(app.CFG, 'General', 'web_use_gzip', 1))
            app.SUBLIMINAL_LOG = bool(check_setting_int(app.CFG, 'General', 'subliminal_log', 0))
            app.PRIVACY_LEVEL = check_setting_str(app.CFG, 'General', 'privacy_level', 'normal')
            app.SSL_VERIFY = bool(check_setting_int(app.CFG, 'General', 'ssl_verify', 1))
            app.SSL_CA_BUNDLE = check_setting_str(app.CFG, 'General', 'ssl_ca_bundle', '')
            app.INDEXER_DEFAULT_LANGUAGE = check_setting_str(app.CFG, 'General', 'indexerDefaultLang', 'en')
            app.TVDB_DVD_ORDER_EP_IGNORE = bool(check_setting_int(app.CFG, 'General', 'tvdb_dvd_order_ep_ignore', 0))
            app.EP_DEFAULT_DELETED_STATUS = check_setting_int(app.CFG, 'General', 'ep_default_deleted_status', 6)
            app.LAUNCH_BROWSER = bool(check_setting_int(app.CFG, 'General', 'launch_browser', 1))
            app.DOWNLOAD_URL = check_setting_str(app.CFG, 'General', 'download_url', '')
            app.LOCALHOST_IP = check_setting_str(app.CFG, 'General', 'localhost_ip', '')
            app.CPU_PRESET = check_setting_str(app.CFG, 'General', 'cpu_preset', 'NORMAL')
            app.ANON_REDIRECT = check_setting_str(app.CFG, 'General', 'anon_redirect', 'http://dereferer.org/?')
            app.PROXY_SETTING = check_setting_str(app.CFG, 'General', 'proxy_setting', '')
            app.PROXY_INDEXERS = bool(check_setting_int(app.CFG, 'General', 'proxy_indexers', 1))

            # attempt to help prevent users from breaking links by using a bad url
            if not app.ANON_REDIRECT.endswith('?'):
                app.ANON_REDIRECT = ''

            app.TRASH_REMOVE_SHOW = bool(check_setting_int(app.CFG, 'General', 'trash_remove_show', 0))
            app.TRASH_ROTATE_LOGS = bool(check_setting_int(app.CFG, 'General', 'trash_rotate_logs', 0))
            app.SORT_ARTICLE = bool(check_setting_int(app.CFG, 'General', 'sort_article', 0))
            app.API_KEY = check_setting_str(app.CFG, 'General', 'api_key', '', censor_log='low')
            app.ENABLE_HTTPS = bool(check_setting_int(app.CFG, 'General', 'enable_https', 0))
            app.NOTIFY_ON_LOGIN = bool(check_setting_int(app.CFG, 'General', 'notify_on_login', 0))
            app.HTTPS_CERT = check_setting_str(app.CFG, 'General', 'https_cert', 'server.crt')
            app.HTTPS_KEY = check_setting_str(app.CFG, 'General', 'https_key', 'server.key')
            app.HANDLE_REVERSE_PROXY = bool(check_setting_int(app.CFG, 'General', 'handle_reverse_proxy', 0))
            app.ROOT_DIRS = check_setting_list(app.CFG, 'General', 'root_dirs')
            app.QUALITY_DEFAULT = check_setting_int(app.CFG, 'General', 'quality_default', SD)
            app.STATUS_DEFAULT = check_setting_int(app.CFG, 'General', 'status_default', SKIPPED)
            app.STATUS_DEFAULT_AFTER = check_setting_int(app.CFG, 'General', 'status_default_after', WANTED)
            app.VERSION_NOTIFY = bool(check_setting_int(app.CFG, 'General', 'version_notify', 1))
            app.AUTO_UPDATE = bool(check_setting_int(app.CFG, 'General', 'auto_update', 0))
            app.NOTIFY_ON_UPDATE = bool(check_setting_int(app.CFG, 'General', 'notify_on_update', 1))
            # TODO: Remove negation, change item name to season_folders_default and default to 1
            app.SEASON_FOLDERS_DEFAULT = not bool(check_setting_int(app.CFG, 'General', 'flatten_folders_default', 0))
            app.INDEXER_DEFAULT = check_setting_int(app.CFG, 'General', 'indexer_default', 0)
            app.INDEXER_TIMEOUT = check_setting_int(app.CFG, 'General', 'indexer_timeout', 20)
            app.ANIME_DEFAULT = bool(check_setting_int(app.CFG, 'General', 'anime_default', 0))
            app.SCENE_DEFAULT = bool(check_setting_int(app.CFG, 'General', 'scene_default', 0))
            app.PROVIDER_ORDER = check_setting_list(app.CFG, 'General', 'provider_order')
            app.NAMING_PATTERN = check_setting_str(app.CFG, 'General', 'naming_pattern', 'Season %0S/%SN - S%0SE%0E - %EN')
            app.NAMING_ABD_PATTERN = check_setting_str(app.CFG, 'General', 'naming_abd_pattern', '%SN - %A.D - %EN')
            app.NAMING_CUSTOM_ABD = bool(check_setting_int(app.CFG, 'General', 'naming_custom_abd', 0))
            app.NAMING_SPORTS_PATTERN = check_setting_str(app.CFG, 'General', 'naming_sports_pattern', '%SN - %A-D - %EN')
            app.NAMING_ANIME_PATTERN = check_setting_str(app.CFG, 'General', 'naming_anime_pattern', 'Season %0S/%SN - S%0SE%0E - %EN')
            app.NAMING_ANIME = check_setting_int(app.CFG, 'General', 'naming_anime', 3)
            app.NAMING_CUSTOM_SPORTS = bool(check_setting_int(app.CFG, 'General', 'naming_custom_sports', 0))
            app.NAMING_CUSTOM_ANIME = bool(check_setting_int(app.CFG, 'General', 'naming_custom_anime', 0))
            app.NAMING_MULTI_EP = check_setting_int(app.CFG, 'General', 'naming_multi_ep', 1)
            app.NAMING_ANIME_MULTI_EP = check_setting_int(app.CFG, 'General', 'naming_anime_multi_ep', 1)
            app.NAMING_FORCE_FOLDERS = naming.check_force_season_folders()
            app.NAMING_STRIP_YEAR = bool(check_setting_int(app.CFG, 'General', 'naming_strip_year', 0))
            app.USE_NZBS = bool(check_setting_int(app.CFG, 'General', 'use_nzbs', 0))
            app.USE_TORRENTS = bool(check_setting_int(app.CFG, 'General', 'use_torrents', 1))

            app.NZB_METHOD = check_setting_str(app.CFG, 'General', 'nzb_method', 'blackhole', valid_values=('blackhole', 'sabnzbd', 'nzbget'))
            app.TORRENT_METHOD = check_setting_str(app.CFG, 'General', 'torrent_method', 'blackhole',
                                                   valid_values=('blackhole', 'utorrent', 'transmission', 'deluge',
                                                                 'deluged', 'downloadstation', 'rtorrent', 'qbittorrent', 'mlnet'))

            app.DOWNLOAD_PROPERS = bool(check_setting_int(app.CFG, 'General', 'download_propers', 1))
            app.PROPERS_SEARCH_DAYS = max(2, min(8, check_setting_int(app.CFG, 'General', 'propers_search_days', 2)))
            app.REMOVE_FROM_CLIENT = bool(check_setting_int(app.CFG, 'General', 'remove_from_client', 0))
            app.CHECK_PROPERS_INTERVAL = check_setting_str(app.CFG, 'General', 'check_propers_interval', '4h',
                                                           valid_values=('15m', '45m', '90m', '4h', 'daily'))
            app.RANDOMIZE_PROVIDERS = bool(check_setting_int(app.CFG, 'General', 'randomize_providers', 0))
            app.ALLOW_HIGH_PRIORITY = bool(check_setting_int(app.CFG, 'General', 'allow_high_priority', 1))
            app.SKIP_REMOVED_FILES = bool(check_setting_int(app.CFG, 'General', 'skip_removed_files', 0))
            app.ALLOWED_EXTENSIONS = check_setting_list(app.CFG, 'General', 'allowed_extensions', app.ALLOWED_EXTENSIONS)
            app.USENET_RETENTION = check_setting_int(app.CFG, 'General', 'usenet_retention', 500)
            app.CACHE_TRIMMING = bool(check_setting_int(app.CFG, 'General', 'cache_trimming', 0))
            app.MAX_CACHE_AGE = check_setting_int(app.CFG, 'General', 'max_cache_age', 30)
            app.AUTOPOSTPROCESSOR_FREQUENCY = max(app.MIN_AUTOPOSTPROCESSOR_FREQUENCY,
                                                  check_setting_int(app.CFG, 'General', 'autopostprocessor_frequency', 10))

            app.TORRENT_CHECKER_FREQUENCY = max(app.MIN_TORRENT_CHECKER_FREQUENCY,
                                                check_setting_int(app.CFG, 'General', 'torrent_checker_frequency',
                                                                  app.DEFAULT_TORRENT_CHECKER_FREQUENCY))
            app.DAILYSEARCH_FREQUENCY = max(app.MIN_DAILYSEARCH_FREQUENCY,
                                            check_setting_int(app.CFG, 'General', 'dailysearch_frequency', app.DEFAULT_DAILYSEARCH_FREQUENCY))
            app.MIN_BACKLOG_FREQUENCY = Application.get_backlog_cycle_time()
            app.BACKLOG_FREQUENCY = max(app.MIN_BACKLOG_FREQUENCY, check_setting_int(app.CFG, 'General', 'backlog_frequency', app.DEFAULT_BACKLOG_FREQUENCY))
            app.UPDATE_FREQUENCY = max(app.MIN_UPDATE_FREQUENCY, check_setting_int(app.CFG, 'General', 'update_frequency', app.DEFAULT_UPDATE_FREQUENCY))
            app.SHOWUPDATE_HOUR = max(0, min(23, check_setting_int(app.CFG, 'General', 'showupdate_hour', app.DEFAULT_SHOWUPDATE_HOUR)))

            app.BACKLOG_DAYS = check_setting_int(app.CFG, 'General', 'backlog_days', 7)

            app.NEWS_LAST_READ = check_setting_str(app.CFG, 'General', 'news_last_read', '1970-01-01')
            app.NEWS_LATEST = app.NEWS_LAST_READ

            app.BROKEN_PROVIDERS = check_setting_list(app.CFG, 'General', 'broken_providers',
                                                      helpers.get_broken_providers() or app.BROKEN_PROVIDERS)

            app.NZB_DIR = check_setting_str(app.CFG, 'Blackhole', 'nzb_dir', '')
            app.TORRENT_DIR = check_setting_str(app.CFG, 'Blackhole', 'torrent_dir', '')

            app.TV_DOWNLOAD_DIR = check_setting_str(app.CFG, 'General', 'tv_download_dir', '')
            app.PROCESS_AUTOMATICALLY = bool(check_setting_int(app.CFG, 'General', 'process_automatically', 0))
            app.NO_DELETE = bool(check_setting_int(app.CFG, 'General', 'no_delete', 0))
            app.UNPACK = bool(check_setting_int(app.CFG, 'General', 'unpack', 0))
            app.RENAME_EPISODES = bool(check_setting_int(app.CFG, 'General', 'rename_episodes', 1))
            app.AIRDATE_EPISODES = bool(check_setting_int(app.CFG, 'General', 'airdate_episodes', 0))
            app.FILE_TIMESTAMP_TIMEZONE = check_setting_str(app.CFG, 'General', 'file_timestamp_timezone', 'network')
            app.KEEP_PROCESSED_DIR = bool(check_setting_int(app.CFG, 'General', 'keep_processed_dir', 1))
            app.PROCESS_METHOD = check_setting_str(app.CFG, 'General', 'process_method', 'copy' if app.KEEP_PROCESSED_DIR else 'move')
            app.DELRARCONTENTS = bool(check_setting_int(app.CFG, 'General', 'del_rar_contents', 0))
            app.MOVE_ASSOCIATED_FILES = bool(check_setting_int(app.CFG, 'General', 'move_associated_files', 0))
            app.POSTPONE_IF_SYNC_FILES = bool(check_setting_int(app.CFG, 'General', 'postpone_if_sync_files', 1))
            app.POSTPONE_IF_NO_SUBS = bool(check_setting_int(app.CFG, 'General', 'postpone_if_no_subs', 0))
            app.SYNC_FILES = check_setting_list(app.CFG, 'General', 'sync_files', app.SYNC_FILES)
            app.NFO_RENAME = bool(check_setting_int(app.CFG, 'General', 'nfo_rename', 1))
            app.CREATE_MISSING_SHOW_DIRS = bool(check_setting_int(app.CFG, 'General', 'create_missing_show_dirs', 0))
            app.ADD_SHOWS_WO_DIR = bool(check_setting_int(app.CFG, 'General', 'add_shows_wo_dir', 0))

            app.NZBS = bool(check_setting_int(app.CFG, 'NZBs', 'nzbs', 0))
            app.NZBS_UID = check_setting_str(app.CFG, 'NZBs', 'nzbs_uid', '', censor_log='normal')
            app.NZBS_HASH = check_setting_str(app.CFG, 'NZBs', 'nzbs_hash', '', censor_log='low')

            app.NEWZBIN = bool(check_setting_int(app.CFG, 'Newzbin', 'newzbin', 0))
            app.NEWZBIN_USERNAME = check_setting_str(app.CFG, 'Newzbin', 'newzbin_username', '', censor_log='normal')
            app.NEWZBIN_PASSWORD = check_setting_str(app.CFG, 'Newzbin', 'newzbin_password', '', censor_log='low')

            app.SAB_USERNAME = check_setting_str(app.CFG, 'SABnzbd', 'sab_username', '', censor_log='normal')
            app.SAB_PASSWORD = check_setting_str(app.CFG, 'SABnzbd', 'sab_password', '', censor_log='low')
            app.SAB_APIKEY = check_setting_str(app.CFG, 'SABnzbd', 'sab_apikey', '', censor_log='low')
            app.SAB_CATEGORY = check_setting_str(app.CFG, 'SABnzbd', 'sab_category', 'tv')
            app.SAB_CATEGORY_BACKLOG = check_setting_str(app.CFG, 'SABnzbd', 'sab_category_backlog', app.SAB_CATEGORY)
            app.SAB_CATEGORY_ANIME = check_setting_str(app.CFG, 'SABnzbd', 'sab_category_anime', 'anime')
            app.SAB_CATEGORY_ANIME_BACKLOG = check_setting_str(app.CFG, 'SABnzbd', 'sab_category_anime_backlog', app.SAB_CATEGORY_ANIME)
            app.SAB_HOST = check_setting_str(app.CFG, 'SABnzbd', 'sab_host', '', censor_log='high')
            app.SAB_FORCED = bool(check_setting_int(app.CFG, 'SABnzbd', 'sab_forced', 0))

            app.NZBGET_USERNAME = check_setting_str(app.CFG, 'NZBget', 'nzbget_username', 'nzbget', censor_log='normal')
            app.NZBGET_PASSWORD = check_setting_str(app.CFG, 'NZBget', 'nzbget_password', 'tegbzn6789', censor_log='low')
            app.NZBGET_CATEGORY = check_setting_str(app.CFG, 'NZBget', 'nzbget_category', 'tv')
            app.NZBGET_CATEGORY_BACKLOG = check_setting_str(app.CFG, 'NZBget', 'nzbget_category_backlog', app.NZBGET_CATEGORY)
            app.NZBGET_CATEGORY_ANIME = check_setting_str(app.CFG, 'NZBget', 'nzbget_category_anime', 'anime')
            app.NZBGET_CATEGORY_ANIME_BACKLOG = check_setting_str(app.CFG, 'NZBget', 'nzbget_category_anime_backlog', app.NZBGET_CATEGORY_ANIME)
            app.NZBGET_HOST = check_setting_str(app.CFG, 'NZBget', 'nzbget_host', '', censor_log='high')
            app.NZBGET_USE_HTTPS = bool(check_setting_int(app.CFG, 'NZBget', 'nzbget_use_https', 0))
            app.NZBGET_PRIORITY = check_setting_int(app.CFG, 'NZBget', 'nzbget_priority', 100)

            app.TORRENT_USERNAME = check_setting_str(app.CFG, 'TORRENT', 'torrent_username', '', censor_log='normal')
            app.TORRENT_PASSWORD = check_setting_str(app.CFG, 'TORRENT', 'torrent_password', '', censor_log='low')
            app.TORRENT_HOST = check_setting_str(app.CFG, 'TORRENT', 'torrent_host', '', censor_log='high')
            app.TORRENT_PATH = check_setting_str(app.CFG, 'TORRENT', 'torrent_path', '')
            app.TORRENT_SEED_TIME = check_setting_int(app.CFG, 'TORRENT', 'torrent_seed_time', 0)
            app.TORRENT_PAUSED = bool(check_setting_int(app.CFG, 'TORRENT', 'torrent_paused', 0))
            app.TORRENT_HIGH_BANDWIDTH = bool(check_setting_int(app.CFG, 'TORRENT', 'torrent_high_bandwidth', 0))
            app.TORRENT_LABEL = check_setting_str(app.CFG, 'TORRENT', 'torrent_label', '')
            app.TORRENT_LABEL_ANIME = check_setting_str(app.CFG, 'TORRENT', 'torrent_label_anime', '')
            app.TORRENT_VERIFY_CERT = bool(check_setting_int(app.CFG, 'TORRENT', 'torrent_verify_cert', 0))
            app.TORRENT_RPCURL = check_setting_str(app.CFG, 'TORRENT', 'torrent_rpcurl', 'transmission')
            app.TORRENT_AUTH_TYPE = check_setting_str(app.CFG, 'TORRENT', 'torrent_auth_type', '')
            app.TORRENT_SEED_LOCATION = check_setting_str(app.CFG, 'TORRENT', 'torrent_seed_location', '')

            app.USE_KODI = bool(check_setting_int(app.CFG, 'KODI', 'use_kodi', 0))
            app.KODI_ALWAYS_ON = bool(check_setting_int(app.CFG, 'KODI', 'kodi_always_on', 1))
            app.KODI_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'KODI', 'kodi_notify_onsnatch', 0))
            app.KODI_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'KODI', 'kodi_notify_ondownload', 0))
            app.KODI_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'KODI', 'kodi_notify_onsubtitledownload', 0))
            app.KODI_UPDATE_LIBRARY = bool(check_setting_int(app.CFG, 'KODI', 'kodi_update_library', 0))
            app.KODI_UPDATE_FULL = bool(check_setting_int(app.CFG, 'KODI', 'kodi_update_full', 0))
            app.KODI_UPDATE_ONLYFIRST = bool(check_setting_int(app.CFG, 'KODI', 'kodi_update_onlyfirst', 0))
            app.KODI_HOST = check_setting_list(app.CFG, 'KODI', 'kodi_host', '', censor_log='high')
            app.KODI_USERNAME = check_setting_str(app.CFG, 'KODI', 'kodi_username', '', censor_log='normal')
            app.KODI_PASSWORD = check_setting_str(app.CFG, 'KODI', 'kodi_password', '', censor_log='low')
            app.KODI_CLEAN_LIBRARY = bool(check_setting_int(app.CFG, 'KODI', 'kodi_clean_library', 0))

            app.USE_PLEX_SERVER = bool(check_setting_int(app.CFG, 'Plex', 'use_plex_server', 0))
            app.PLEX_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Plex', 'plex_notify_onsnatch', 0))
            app.PLEX_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Plex', 'plex_notify_ondownload', 0))
            app.PLEX_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Plex', 'plex_notify_onsubtitledownload', 0))
            app.PLEX_UPDATE_LIBRARY = bool(check_setting_int(app.CFG, 'Plex', 'plex_update_library', 0))
            app.PLEX_SERVER_HOST = check_setting_list(app.CFG, 'Plex', 'plex_server_host', '', censor_log='high')
            app.PLEX_SERVER_TOKEN = check_setting_str(app.CFG, 'Plex', 'plex_server_token', '', censor_log='high')
            app.PLEX_CLIENT_HOST = check_setting_list(app.CFG, 'Plex', 'plex_client_host', '', censor_log='high')
            app.PLEX_SERVER_USERNAME = check_setting_str(app.CFG, 'Plex', 'plex_server_username', '', censor_log='normal')
            app.PLEX_SERVER_PASSWORD = check_setting_str(app.CFG, 'Plex', 'plex_server_password', '', censor_log='low')
            app.USE_PLEX_CLIENT = bool(check_setting_int(app.CFG, 'Plex', 'use_plex_client', 0))
            app.PLEX_CLIENT_USERNAME = check_setting_str(app.CFG, 'Plex', 'plex_client_username', '', censor_log='normal')
            app.PLEX_CLIENT_PASSWORD = check_setting_str(app.CFG, 'Plex', 'plex_client_password', '', censor_log='low')
            app.PLEX_SERVER_HTTPS = bool(check_setting_int(app.CFG, 'Plex', 'plex_server_https', 0))

            app.USE_EMBY = bool(check_setting_int(app.CFG, 'Emby', 'use_emby', 0))
            app.EMBY_HOST = check_setting_str(app.CFG, 'Emby', 'emby_host', '', censor_log='high')
            app.EMBY_APIKEY = check_setting_str(app.CFG, 'Emby', 'emby_apikey', '', censor_log='low')

            app.USE_GROWL = bool(check_setting_int(app.CFG, 'Growl', 'use_growl', 0))
            app.GROWL_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Growl', 'growl_notify_onsnatch', 0))
            app.GROWL_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Growl', 'growl_notify_ondownload', 0))
            app.GROWL_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Growl', 'growl_notify_onsubtitledownload', 0))
            app.GROWL_HOST = check_setting_str(app.CFG, 'Growl', 'growl_host', '')
            app.GROWL_PASSWORD = check_setting_str(app.CFG, 'Growl', 'growl_password', '', censor_log='low')

            app.USE_FREEMOBILE = bool(check_setting_int(app.CFG, 'FreeMobile', 'use_freemobile', 0))
            app.FREEMOBILE_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'FreeMobile', 'freemobile_notify_onsnatch', 0))
            app.FREEMOBILE_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'FreeMobile', 'freemobile_notify_ondownload', 0))
            app.FREEMOBILE_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'FreeMobile', 'freemobile_notify_onsubtitledownload', 0))
            app.FREEMOBILE_ID = check_setting_str(app.CFG, 'FreeMobile', 'freemobile_id', '', censor_log='normal')
            app.FREEMOBILE_APIKEY = check_setting_str(app.CFG, 'FreeMobile', 'freemobile_apikey', '', censor_log='low')

            app.USE_TELEGRAM = bool(check_setting_int(app.CFG, 'Telegram', 'use_telegram', 0))
            app.TELEGRAM_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Telegram', 'telegram_notify_onsnatch', 0))
            app.TELEGRAM_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Telegram', 'telegram_notify_ondownload', 0))
            app.TELEGRAM_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Telegram', 'telegram_notify_onsubtitledownload', 0))
            app.TELEGRAM_ID = check_setting_str(app.CFG, 'Telegram', 'telegram_id', '', censor_log='normal')
            app.TELEGRAM_APIKEY = check_setting_str(app.CFG, 'Telegram', 'telegram_apikey', '', censor_log='low')

            app.USE_PROWL = bool(check_setting_int(app.CFG, 'Prowl', 'use_prowl', 0))
            app.PROWL_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Prowl', 'prowl_notify_onsnatch', 0))
            app.PROWL_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Prowl', 'prowl_notify_ondownload', 0))
            app.PROWL_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Prowl', 'prowl_notify_onsubtitledownload', 0))
            app.PROWL_API = check_setting_list(app.CFG, 'Prowl', 'prowl_api', '', censor_log='low')
            app.PROWL_PRIORITY = check_setting_str(app.CFG, 'Prowl', 'prowl_priority', '0')
            app.PROWL_MESSAGE_TITLE = check_setting_str(app.CFG, 'Prowl', 'prowl_message_title', 'Medusa')

            app.USE_TWITTER = bool(check_setting_int(app.CFG, 'Twitter', 'use_twitter', 0))
            app.TWITTER_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Twitter', 'twitter_notify_onsnatch', 0))
            app.TWITTER_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Twitter', 'twitter_notify_ondownload', 0))
            app.TWITTER_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Twitter', 'twitter_notify_onsubtitledownload', 0))
            app.TWITTER_USERNAME = check_setting_str(app.CFG, 'Twitter', 'twitter_username', '', censor_log='normal')
            app.TWITTER_PASSWORD = check_setting_str(app.CFG, 'Twitter', 'twitter_password', '', censor_log='low')
            app.TWITTER_PREFIX = check_setting_str(app.CFG, 'Twitter', 'twitter_prefix', app.GIT_REPO)
            app.TWITTER_DMTO = check_setting_str(app.CFG, 'Twitter', 'twitter_dmto', '')
            app.TWITTER_USEDM = bool(check_setting_int(app.CFG, 'Twitter', 'twitter_usedm', 0))

            app.USE_BOXCAR2 = bool(check_setting_int(app.CFG, 'Boxcar2', 'use_boxcar2', 0))
            app.BOXCAR2_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Boxcar2', 'boxcar2_notify_onsnatch', 0))
            app.BOXCAR2_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Boxcar2', 'boxcar2_notify_ondownload', 0))
            app.BOXCAR2_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Boxcar2', 'boxcar2_notify_onsubtitledownload', 0))
            app.BOXCAR2_ACCESSTOKEN = check_setting_str(app.CFG, 'Boxcar2', 'boxcar2_accesstoken', '', censor_log='low')

            app.USE_PUSHOVER = bool(check_setting_int(app.CFG, 'Pushover', 'use_pushover', 0))
            app.PUSHOVER_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Pushover', 'pushover_notify_onsnatch', 0))
            app.PUSHOVER_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushover', 'pushover_notify_ondownload', 0))
            app.PUSHOVER_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushover', 'pushover_notify_onsubtitledownload', 0))
            app.PUSHOVER_USERKEY = check_setting_str(app.CFG, 'Pushover', 'pushover_userkey', '', censor_log='normal')
            app.PUSHOVER_APIKEY = check_setting_str(app.CFG, 'Pushover', 'pushover_apikey', '', censor_log='low')
            app.PUSHOVER_DEVICE = check_setting_list(app.CFG, 'Pushover', 'pushover_device', '')
            app.PUSHOVER_SOUND = check_setting_str(app.CFG, 'Pushover', 'pushover_sound', 'default')
            app.PUSHOVER_PRIORITY = check_setting_str(app.CFG, 'Pushover', 'pushover_priority', '0')

            app.USE_LIBNOTIFY = bool(check_setting_int(app.CFG, 'Libnotify', 'use_libnotify', 0))
            app.LIBNOTIFY_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Libnotify', 'libnotify_notify_onsnatch', 0))
            app.LIBNOTIFY_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Libnotify', 'libnotify_notify_ondownload', 0))
            app.LIBNOTIFY_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Libnotify', 'libnotify_notify_onsubtitledownload', 0))

            app.USE_NMJ = bool(check_setting_int(app.CFG, 'NMJ', 'use_nmj', 0))
            app.NMJ_HOST = check_setting_str(app.CFG, 'NMJ', 'nmj_host', '')
            app.NMJ_DATABASE = check_setting_str(app.CFG, 'NMJ', 'nmj_database', '')
            app.NMJ_MOUNT = check_setting_str(app.CFG, 'NMJ', 'nmj_mount', '')

            app.USE_NMJv2 = bool(check_setting_int(app.CFG, 'NMJv2', 'use_nmjv2', 0))
            app.NMJv2_HOST = check_setting_str(app.CFG, 'NMJv2', 'nmjv2_host', '')
            app.NMJv2_DATABASE = check_setting_str(app.CFG, 'NMJv2', 'nmjv2_database', '')
            app.NMJv2_DBLOC = check_setting_str(app.CFG, 'NMJv2', 'nmjv2_dbloc', '')

            app.USE_SYNOINDEX = bool(check_setting_int(app.CFG, 'Synology', 'use_synoindex', 0))

            app.USE_SYNOLOGYNOTIFIER = bool(check_setting_int(app.CFG, 'SynologyNotifier', 'use_synologynotifier', 0))
            app.SYNOLOGYNOTIFIER_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'SynologyNotifier', 'synologynotifier_notify_onsnatch', 0))
            app.SYNOLOGYNOTIFIER_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'SynologyNotifier', 'synologynotifier_notify_ondownload', 0))
            app.SYNOLOGYNOTIFIER_NOTIFY_ONSUBTITLEDOWNLOAD = bool(
                check_setting_int(app.CFG, 'SynologyNotifier', 'synologynotifier_notify_onsubtitledownload', 0))

            app.USE_SLACK = bool(check_setting_bool(app.CFG, 'Slack', 'use_slack', 0))
            app.SLACK_NOTIFY_SNATCH = bool(check_setting_bool(app.CFG, 'Slack', 'slack_notify_snatch', 0))
            app.SLACK_NOTIFY_DOWNLOAD = bool(check_setting_bool(app.CFG, 'Slack', 'slack_notify_download', 0))
            app.SLACK_NOTIFY_SUBTITLEDOWNLOAD = bool(check_setting_bool(app.CFG, 'Slack', 'slack_notify_onsubtitledownload', 0))
            app.SLACK_WEBHOOK = check_setting_str(app.CFG, 'Slack', 'slack_webhook', '', censor_log='normal')

            app.USE_TRAKT = bool(check_setting_int(app.CFG, 'Trakt', 'use_trakt', 0))
            app.TRAKT_USERNAME = check_setting_str(app.CFG, 'Trakt', 'trakt_username', '', censor_log='normal')
            app.TRAKT_ACCESS_TOKEN = check_setting_str(app.CFG, 'Trakt', 'trakt_access_token', '', censor_log='low')
            app.TRAKT_REFRESH_TOKEN = check_setting_str(app.CFG, 'Trakt', 'trakt_refresh_token', '', censor_log='low')
            app.TRAKT_REMOVE_WATCHLIST = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_remove_watchlist', 0))
            app.TRAKT_REMOVE_SERIESLIST = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_remove_serieslist', 0))

            # Check if user has legacy setting and store value in new setting
            if check_setting_int(app.CFG, 'Trakt', 'trakt_remove_show_from_sickrage', None) is not None:
                app.TRAKT_REMOVE_SHOW_FROM_APPLICATION = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_remove_show_from_sickrage', 0))
            else:
                app.TRAKT_REMOVE_SHOW_FROM_APPLICATION = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_remove_show_from_application', 0))

            app.TRAKT_SYNC_WATCHLIST = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_sync_watchlist', 0))
            app.TRAKT_METHOD_ADD = check_setting_int(app.CFG, 'Trakt', 'trakt_method_add', 0)
            app.TRAKT_START_PAUSED = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_start_paused', 0))
            app.TRAKT_USE_RECOMMENDED = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_use_recommended', 0))
            app.TRAKT_SYNC = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_sync', 0))
            app.TRAKT_SYNC_REMOVE = bool(check_setting_int(app.CFG, 'Trakt', 'trakt_sync_remove', 0))
            app.TRAKT_DEFAULT_INDEXER = check_setting_int(app.CFG, 'Trakt', 'trakt_default_indexer', INDEXER_TVDBV2)
            if app.TRAKT_DEFAULT_INDEXER == INDEXER_TVMAZE:
                # Trakt doesn't support TVMAZE. Default to TVDB
                app.TRAKT_DEFAULT_INDEXER = INDEXER_TVDBV2
            app.TRAKT_TIMEOUT = check_setting_int(app.CFG, 'Trakt', 'trakt_timeout', 30)
            app.TRAKT_BLACKLIST_NAME = check_setting_str(app.CFG, 'Trakt', 'trakt_blacklist_name', '')

            app.USE_PYTIVO = bool(check_setting_int(app.CFG, 'pyTivo', 'use_pytivo', 0))
            app.PYTIVO_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'pyTivo', 'pytivo_notify_onsnatch', 0))
            app.PYTIVO_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'pyTivo', 'pytivo_notify_ondownload', 0))
            app.PYTIVO_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'pyTivo', 'pytivo_notify_onsubtitledownload', 0))
            app.PYTIVO_UPDATE_LIBRARY = bool(check_setting_int(app.CFG, 'pyTivo', 'pyTivo_update_library', 0))
            app.PYTIVO_HOST = check_setting_str(app.CFG, 'pyTivo', 'pytivo_host', '')
            app.PYTIVO_SHARE_NAME = check_setting_str(app.CFG, 'pyTivo', 'pytivo_share_name', '')
            app.PYTIVO_TIVO_NAME = check_setting_str(app.CFG, 'pyTivo', 'pytivo_tivo_name', '')

            app.USE_PUSHALOT = bool(check_setting_int(app.CFG, 'Pushalot', 'use_pushalot', 0))
            app.PUSHALOT_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Pushalot', 'pushalot_notify_onsnatch', 0))
            app.PUSHALOT_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushalot', 'pushalot_notify_ondownload', 0))
            app.PUSHALOT_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushalot', 'pushalot_notify_onsubtitledownload', 0))
            app.PUSHALOT_AUTHORIZATIONTOKEN = check_setting_str(app.CFG, 'Pushalot', 'pushalot_authorizationtoken', '', censor_log='low')

            app.USE_PUSHBULLET = bool(check_setting_int(app.CFG, 'Pushbullet', 'use_pushbullet', 0))
            app.PUSHBULLET_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Pushbullet', 'pushbullet_notify_onsnatch', 0))
            app.PUSHBULLET_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushbullet', 'pushbullet_notify_ondownload', 0))
            app.PUSHBULLET_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Pushbullet', 'pushbullet_notify_onsubtitledownload', 0))
            app.PUSHBULLET_API = check_setting_str(app.CFG, 'Pushbullet', 'pushbullet_api', '', censor_log='low')
            app.PUSHBULLET_DEVICE = check_setting_str(app.CFG, 'Pushbullet', 'pushbullet_device', '')

            app.USE_JOIN = bool(check_setting_int(app.CFG, 'Join', 'use_join', 0))
            app.JOIN_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Join', 'join_notify_onsnatch', 0))
            app.JOIN_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Join', 'join_notify_ondownload', 0))
            app.JOIN_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Join', 'join_notify_onsubtitledownload', 0))
            app.JOIN_API = check_setting_str(app.CFG, 'Join', 'join_api', '', censor_log='low')
            app.JOIN_DEVICE = check_setting_str(app.CFG, 'Join', 'join_device', '')

            app.USE_EMAIL = bool(check_setting_int(app.CFG, 'Email', 'use_email', 0))
            app.EMAIL_NOTIFY_ONSNATCH = bool(check_setting_int(app.CFG, 'Email', 'email_notify_onsnatch', 0))
            app.EMAIL_NOTIFY_ONDOWNLOAD = bool(check_setting_int(app.CFG, 'Email', 'email_notify_ondownload', 0))
            app.EMAIL_NOTIFY_ONSUBTITLEDOWNLOAD = bool(check_setting_int(app.CFG, 'Email', 'email_notify_onsubtitledownload', 0))
            app.EMAIL_HOST = check_setting_str(app.CFG, 'Email', 'email_host', '')
            app.EMAIL_PORT = check_setting_int(app.CFG, 'Email', 'email_port', 25)
            app.EMAIL_TLS = bool(check_setting_int(app.CFG, 'Email', 'email_tls', 0))
            app.EMAIL_USER = check_setting_str(app.CFG, 'Email', 'email_user', '', censor_log='normal')
            app.EMAIL_PASSWORD = check_setting_str(app.CFG, 'Email', 'email_password', '', censor_log='low')
            app.EMAIL_FROM = check_setting_str(app.CFG, 'Email', 'email_from', '')
            app.EMAIL_LIST = check_setting_list(app.CFG, 'Email', 'email_list', '')
            app.EMAIL_SUBJECT = check_setting_str(app.CFG, 'Email', 'email_subject', '')

            app.USE_SUBTITLES = bool(check_setting_int(app.CFG, 'Subtitles', 'use_subtitles', 0))
            app.SUBTITLES_ERASE_CACHE = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_erase_cache', 0))
            app.SUBTITLES_LANGUAGES = check_setting_list(app.CFG, 'Subtitles', 'subtitles_languages')
            app.SUBTITLES_DIR = check_setting_str(app.CFG, 'Subtitles', 'subtitles_dir', '')
            app.SUBTITLES_SERVICES_LIST = check_setting_list(app.CFG, 'Subtitles', 'SUBTITLES_SERVICES_LIST')
            app.SUBTITLES_SERVICES_ENABLED = check_setting_list(app.CFG, 'Subtitles', 'SUBTITLES_SERVICES_ENABLED', transform=int)
            app.SUBTITLES_DEFAULT = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_default', 0))
            app.SUBTITLES_HISTORY = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_history', 0))
            app.SUBTITLES_PERFECT_MATCH = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_perfect_match', 1))
            app.IGNORE_EMBEDDED_SUBS = bool(check_setting_int(app.CFG, 'Subtitles', 'embedded_subtitles_all', 0))
            app.SUBTITLES_STOP_AT_FIRST = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_stop_at_first', 0))
            app.ACCEPT_UNKNOWN_EMBEDDED_SUBS = bool(check_setting_int(app.CFG, 'Subtitles', 'embedded_subtitles_unknown_lang', 0))
            app.SUBTITLES_HEARING_IMPAIRED = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_hearing_impaired', 0))
            app.SUBTITLES_FINDER_FREQUENCY = check_setting_int(app.CFG, 'Subtitles', 'subtitles_finder_frequency', 1)
            app.SUBTITLES_MULTI = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_multi', 1))
            app.SUBTITLES_KEEP_ONLY_WANTED = bool(check_setting_int(app.CFG, 'Subtitles', 'subtitles_keep_only_wanted', 0))
            app.SUBTITLES_EXTRA_SCRIPTS = [x.strip() for x in check_setting_list(app.CFG, 'Subtitles', 'subtitles_extra_scripts', '')]
            app.SUBTITLES_PRE_SCRIPTS = [x.strip() for x in check_setting_list(app.CFG, 'Subtitles', 'subtitles_pre_scripts', '')]

            app.ADDIC7ED_USER = check_setting_str(app.CFG, 'Subtitles', 'addic7ed_username', '', censor_log='normal')
            app.ADDIC7ED_PASS = check_setting_str(app.CFG, 'Subtitles', 'addic7ed_password', '', censor_log='low')

            app.ITASA_USER = check_setting_str(app.CFG, 'Subtitles', 'itasa_username', '', censor_log='normal')
            app.ITASA_PASS = check_setting_str(app.CFG, 'Subtitles', 'itasa_password', '', censor_log='low')

            app.LEGENDASTV_USER = check_setting_str(app.CFG, 'Subtitles', 'legendastv_username', '', censor_log='normal')
            app.LEGENDASTV_PASS = check_setting_str(app.CFG, 'Subtitles', 'legendastv_password', '', censor_log='low')

            app.OPENSUBTITLES_USER = check_setting_str(app.CFG, 'Subtitles', 'opensubtitles_username', '', censor_log='normal')
            app.OPENSUBTITLES_PASS = check_setting_str(app.CFG, 'Subtitles', 'opensubtitles_password', '', censor_log='low')

            app.USE_FAILED_DOWNLOADS = bool(check_setting_int(app.CFG, 'FailedDownloads', 'use_failed_downloads', 0))
            app.DELETE_FAILED = bool(check_setting_int(app.CFG, 'FailedDownloads', 'delete_failed', 0))

            app.GIT_PATH = check_setting_str(app.CFG, 'General', 'git_path', '')

            app.IGNORE_WORDS = check_setting_list(app.CFG, 'General', 'ignore_words', app.IGNORE_WORDS)
            app.PREFERRED_WORDS = check_setting_list(app.CFG, 'General', 'preferred_words', app.PREFERRED_WORDS)
            app.UNDESIRED_WORDS = check_setting_list(app.CFG, 'General', 'undesired_words', app.UNDESIRED_WORDS)
            app.TRACKERS_LIST = check_setting_list(app.CFG, 'General', 'trackers_list', app.TRACKERS_LIST)
            app.REQUIRE_WORDS = check_setting_list(app.CFG, 'General', 'require_words', app.REQUIRE_WORDS)
            app.IGNORED_SUBS_LIST = check_setting_list(app.CFG, 'General', 'ignored_subs_list', app.IGNORED_SUBS_LIST)
            app.IGNORE_UND_SUBS = bool(check_setting_int(app.CFG, 'General', 'ignore_und_subs', app.IGNORE_UND_SUBS))

            app.CALENDAR_UNPROTECTED = bool(check_setting_int(app.CFG, 'General', 'calendar_unprotected', 0))
            app.CALENDAR_ICONS = bool(check_setting_int(app.CFG, 'General', 'calendar_icons', 0))

            app.NO_RESTART = bool(check_setting_int(app.CFG, 'General', 'no_restart', 0))

            app.EXTRA_SCRIPTS = [x.strip() for x in check_setting_list(app.CFG, 'General', 'extra_scripts')]

            app.USE_LISTVIEW = bool(check_setting_int(app.CFG, 'General', 'use_listview', 0))

            app.ANIMESUPPORT = False
            app.USE_ANIDB = bool(check_setting_int(app.CFG, 'ANIDB', 'use_anidb', 0))
            app.ANIDB_USERNAME = check_setting_str(app.CFG, 'ANIDB', 'anidb_username', '', censor_log='normal')
            app.ANIDB_PASSWORD = check_setting_str(app.CFG, 'ANIDB', 'anidb_password', '', censor_log='low')
            app.ANIDB_USE_MYLIST = bool(check_setting_int(app.CFG, 'ANIDB', 'anidb_use_mylist', 0))
            app.ANIME_SPLIT_HOME = bool(check_setting_int(app.CFG, 'ANIME', 'anime_split_home', 0))
            app.ANIME_SPLIT_HOME_IN_TABS = bool(check_setting_int(app.CFG, 'ANIME', 'anime_split_home_in_tabs', 0))

            app.METADATA_KODI = check_setting_list(app.CFG, 'General', 'metadata_kodi', ['0'] * 10, transform=int)
            app.METADATA_KODI_12PLUS = check_setting_list(app.CFG, 'General', 'metadata_kodi_12plus', ['0'] * 10, transform=int)
            app.METADATA_MEDIABROWSER = check_setting_list(app.CFG, 'General', 'metadata_mediabrowser', ['0'] * 10, transform=int)
            app.METADATA_PS3 = check_setting_list(app.CFG, 'General', 'metadata_ps3', ['0'] * 10, transform=int)
            app.METADATA_WDTV = check_setting_list(app.CFG, 'General', 'metadata_wdtv', ['0'] * 10, transform=int)
            app.METADATA_TIVO = check_setting_list(app.CFG, 'General', 'metadata_tivo', ['0'] * 10, transform=int)
            app.METADATA_MEDE8ER = check_setting_list(app.CFG, 'General', 'metadata_mede8er', ['0'] * 10, transform=int)

            app.HOME_LAYOUT = check_setting_str(app.CFG, 'GUI', 'home_layout', 'poster')
            app.HISTORY_LAYOUT = check_setting_str(app.CFG, 'GUI', 'history_layout', 'detailed')
            app.HISTORY_LIMIT = check_setting_str(app.CFG, 'GUI', 'history_limit', '100')
            app.DISPLAY_SHOW_SPECIALS = bool(check_setting_int(app.CFG, 'GUI', 'display_show_specials', 1))
            app.COMING_EPS_LAYOUT = check_setting_str(app.CFG, 'GUI', 'coming_eps_layout', 'banner')
            app.COMING_EPS_DISPLAY_PAUSED = bool(check_setting_int(app.CFG, 'GUI', 'coming_eps_display_paused', 0))
            app.COMING_EPS_SORT = check_setting_str(app.CFG, 'GUI', 'coming_eps_sort', 'date')
            app.COMING_EPS_MISSED_RANGE = check_setting_int(app.CFG, 'GUI', 'coming_eps_missed_range', 7)
            app.FUZZY_DATING = bool(check_setting_int(app.CFG, 'GUI', 'fuzzy_dating', 0))
            app.TRIM_ZERO = bool(check_setting_int(app.CFG, 'GUI', 'trim_zero', 0))
            app.DATE_PRESET = check_setting_str(app.CFG, 'GUI', 'date_preset', '%x')
            app.TIME_PRESET_W_SECONDS = check_setting_str(app.CFG, 'GUI', 'time_preset', '%I:%M:%S %p')
            app.TIME_PRESET = app.TIME_PRESET_W_SECONDS.replace(u':%S', u'')
            app.TIMEZONE_DISPLAY = check_setting_str(app.CFG, 'GUI', 'timezone_display', 'local')
            app.POSTER_SORTBY = check_setting_str(app.CFG, 'GUI', 'poster_sortby', 'name')
            app.POSTER_SORTDIR = check_setting_int(app.CFG, 'GUI', 'poster_sortdir', 1)
            app.DISPLAY_ALL_SEASONS = bool(check_setting_int(app.CFG, 'General', 'display_all_seasons', 1))
            app.RECENTLY_DELETED = set()
            app.RELEASES_IN_PP = []
            app.GIT_REMOTE_BRANCHES = []
            app.KODI_LIBRARY_CLEAN_PENDING = False
            app.SELECTED_ROOT = check_setting_int(app.CFG, 'GUI', 'selected_root', -1)
            app.BACKLOG_PERIOD = check_setting_str(app.CFG, 'GUI', 'backlog_period', 'all')
            app.BACKLOG_STATUS = check_setting_str(app.CFG, 'GUI', 'backlog_status', 'all')
            app.LAYOUT_WIDE = check_setting_bool(app.CFG, 'GUI', 'layout_wide', 0)
            app.SHOW_LIST_ORDER = check_setting_list(app.CFG, 'GUI', 'show_list_order', app.SHOW_LIST_ORDER)

            app.FALLBACK_PLEX_ENABLE = check_setting_int(app.CFG, 'General', 'fallback_plex_enable', 1)
            app.FALLBACK_PLEX_NOTIFICATIONS = check_setting_int(app.CFG, 'General', 'fallback_plex_notifications', 1)
            app.FALLBACK_PLEX_TIMEOUT = check_setting_int(app.CFG, 'General', 'fallback_plex_timeout', 3)

            # reconfigure the logger
            app_logger.reconfigure()

            # initialize static configuration
            try:
                import pwd
                app.OS_USER = pwd.getpwuid(os.getuid()).pw_name
            except ImportError:
                try:
                    import getpass
                    app.OS_USER = getpass.getuser()
                except Exception:
                    pass

            try:
                app.LOCALE = locale.getdefaultlocale()
            except Exception:
                app.LOCALE = None, None

            try:
                import ssl
                app.OPENSSL_VERSION = ssl.OPENSSL_VERSION
            except Exception:
                pass

            if app.VERSION_NOTIFY:
                updater = version_checker.CheckVersion().updater
                if updater:
                    app.APP_VERSION = updater.get_cur_version()

            app.MAJOR_DB_VERSION, app.MINOR_DB_VERSION = db.DBConnection().checkDBVersion()

            # initialize the static NZB and TORRENT providers
            app.providerList = providers.make_provider_list()

            app.NEWZNAB_PROVIDERS = check_setting_list(app.CFG, 'Newznab', 'newznab_providers')
            app.newznabProviderList = NewznabProvider.get_newznab_providers(app.NEWZNAB_PROVIDERS)

            app.TORRENTRSS_PROVIDERS = check_setting_list(app.CFG, 'TorrentRss', 'torrentrss_providers')
            app.torrentRssProviderList = TorrentRssProvider.get_providers_list(app.TORRENTRSS_PROVIDERS)

            app.TORZNAB_PROVIDERS = check_setting_list(app.CFG, 'Torznab', 'torznab_providers')
            app.torznab_providers_list = TorznabProvider.get_providers_list(app.TORZNAB_PROVIDERS)

            all_providers = providers.sorted_provider_list()

            # dynamically load provider settings
            for provider in all_providers:
                # use check_setting_bool to see if the provider is enabled instead of load_provider_settings
                # since the attr name does not match the default provider option style of '{provider}_{attribute}'
                provider.enabled = check_setting_bool(app.CFG, provider.get_id().upper(), provider.get_id(), 0)

                load_provider_setting(app.CFG, provider, 'string', 'username', '', censor_log='normal')
                load_provider_setting(app.CFG, provider, 'string', 'api_key', '', censor_log='low')
                load_provider_setting(app.CFG, provider, 'string', 'search_mode', 'eponly')
                load_provider_setting(app.CFG, provider, 'bool', 'search_fallback', 0)
                load_provider_setting(app.CFG, provider, 'bool', 'enable_daily', 1)
                load_provider_setting(app.CFG, provider, 'bool', 'enable_backlog', provider.supports_backlog)
                load_provider_setting(app.CFG, provider, 'bool', 'enable_manualsearch', 1)
                load_provider_setting(app.CFG, provider, 'bool', 'enable_search_delay', 0)
                load_provider_setting(app.CFG, provider, 'int', 'search_delay', 480)

                if provider.provider_type == GenericProvider.TORRENT:
                    load_provider_setting(app.CFG, provider, 'string', 'custom_url', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'hash', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'digest', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'password', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'passkey', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'pin', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'sorting', 'seeders')
                    load_provider_setting(app.CFG, provider, 'string', 'options', '')
                    load_provider_setting(app.CFG, provider, 'string', 'ratio', '')
                    load_provider_setting(app.CFG, provider, 'bool', 'confirmed', 1)
                    load_provider_setting(app.CFG, provider, 'bool', 'ranked', 1)
                    load_provider_setting(app.CFG, provider, 'bool', 'engrelease', 0)
                    load_provider_setting(app.CFG, provider, 'bool', 'onlyspasearch', 0)
                    load_provider_setting(app.CFG, provider, 'int', 'minseed', 1)
                    load_provider_setting(app.CFG, provider, 'int', 'minleech', 0)
                    load_provider_setting(app.CFG, provider, 'bool', 'freeleech', 0)
                    load_provider_setting(app.CFG, provider, 'int', 'cat', 0)
                    load_provider_setting(app.CFG, provider, 'bool', 'subtitle', 0)
                    if provider.enable_cookies:
                        load_provider_setting(app.CFG, provider, 'string', 'cookies', '', censor_log='low')

                if isinstance(provider, TorrentRssProvider):
                    load_provider_setting(app.CFG, provider, 'string', 'url', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'string', 'title_tag', '')

                if isinstance(provider, TorznabProvider):
                    load_provider_setting(app.CFG, provider, 'string', 'url', '', censor_log='low')
                    load_provider_setting(app.CFG, provider, 'list', 'cat_ids', '', split_value=',')
                    load_provider_setting(app.CFG, provider, 'list', 'cap_tv_search', '', split_value=',')

                if isinstance(provider, NewznabProvider):
                    # non configurable
                    if not provider.default:
                        load_provider_setting(app.CFG, provider, 'string', 'url', '', censor_log='low')
                        load_provider_setting(app.CFG, provider, 'bool', 'needs_auth', 1)
                    # configurable
                    load_provider_setting(app.CFG, provider, 'list', 'cat_ids', '', split_value=',')

            if not os.path.isfile(app.CONFIG_FILE):
                logger.debug(u'Unable to find {config!r}, all settings will be default!', config=app.CONFIG_FILE)
                self.save_config()

            if app.SUBTITLES_ERASE_CACHE:
                try:
                    for cache_file in ['application.dbm', 'subliminal.dbm']:
                        file_path = os.path.join(app.CACHE_DIR, cache_file)
                        if os.path.isfile(file_path):
                            logger.info(u'Removing subtitles cache file: {cache_file}', cache_file=file_path)
                            os.remove(file_path)
                except OSError as e:
                    logger.warning(u'Unable to remove subtitles cache files. Error: {error}', error=e)
                # Disable flag to erase cache
                app.SUBTITLES_ERASE_CACHE = False

            # Check if we start with a different Python version since last start
            python_version_changed = self.migrate_python_version()

            # Check if we need to perform a restore of the cache folder
            Application.restore_cache_folder(app.CACHE_DIR)
            cache.configure(app.CACHE_DIR, replace=python_version_changed)

            # Rebuild the censored list
            app_logger.rebuild_censored_list()

            # initialize the main SB database
            main_db_con = db.DBConnection()
            db.upgradeDatabase(main_db_con, main_db.InitialSchema)

            # initialize the cache database
            cache_db_con = db.DBConnection('cache.db')
            db.upgradeDatabase(cache_db_con, cache_db.InitialSchema)

            # Performs a vacuum on cache.db
            logger.debug(u'Performing a vacuum on the CACHE database')
            cache_db_con.action('VACUUM')

            # initialize the failed downloads database
            failed_db_con = db.DBConnection('failed.db')
            db.upgradeDatabase(failed_db_con, failed_db.InitialSchema)

            # fix up any db problems
            main_db_con = db.DBConnection()
            db.sanityCheckDatabase(main_db_con, main_db.MainSanityCheck)

            # migrate the config if it needs it
            migrator = ConfigMigrator(app.CFG)
            migrator.migrate_config()

            # initialize metadata_providers
            app.metadata_provider_dict = metadata.get_metadata_generator_dict()
            for cur_metadata_tuple in [(app.METADATA_KODI, metadata.kodi),
                                       (app.METADATA_KODI_12PLUS, metadata.kodi_12plus),
                                       (app.METADATA_MEDIABROWSER, metadata.media_browser),
                                       (app.METADATA_PS3, metadata.ps3),
                                       (app.METADATA_WDTV, metadata.wdtv),
                                       (app.METADATA_TIVO, metadata.tivo),
                                       (app.METADATA_MEDE8ER, metadata.mede8er)]:
                (cur_metadata_config, cur_metadata_class) = cur_metadata_tuple
                tmp_provider = cur_metadata_class.metadata_class()
                tmp_provider.set_config(cur_metadata_config)
                app.metadata_provider_dict[tmp_provider.name] = tmp_provider

            # initialize schedulers
            # updaters
            app.version_check_scheduler = scheduler.Scheduler(version_checker.CheckVersion(),
                                                              cycleTime=datetime.timedelta(hours=app.UPDATE_FREQUENCY),
                                                              threadName='CHECKVERSION', silent=False)

            app.show_queue_scheduler = scheduler.Scheduler(show_queue.ShowQueue(),
                                                           cycleTime=datetime.timedelta(seconds=3),
                                                           threadName='SHOWQUEUE')

            app.show_update_scheduler = scheduler.Scheduler(show_updater.ShowUpdater(),
                                                            cycleTime=datetime.timedelta(hours=1),
                                                            threadName='SHOWUPDATER',
                                                            start_time=datetime.time(hour=app.SHOWUPDATE_HOUR,
                                                                                     minute=random.randint(0, 59)))

            # snatcher used for manual search, manual picked results
            app.manual_snatch_scheduler = scheduler.Scheduler(SnatchQueue(),
                                                              cycleTime=datetime.timedelta(seconds=3),
                                                              threadName='MANUALSNATCHQUEUE')
            # searchers
            app.search_queue_scheduler = scheduler.Scheduler(SearchQueue(),
                                                             cycleTime=datetime.timedelta(seconds=3),
                                                             threadName='SEARCHQUEUE')

            app.forced_search_queue_scheduler = scheduler.Scheduler(ForcedSearchQueue(),
                                                                    cycleTime=datetime.timedelta(seconds=3),
                                                                    threadName='FORCEDSEARCHQUEUE')

            # TODO: update_interval should take last daily/backlog times into account!
            update_interval = datetime.timedelta(minutes=app.DAILYSEARCH_FREQUENCY)
            app.daily_search_scheduler = scheduler.Scheduler(DailySearcher(),
                                                             cycleTime=update_interval,
                                                             threadName='DAILYSEARCHER',
                                                             run_delay=update_interval)

            update_interval = datetime.timedelta(minutes=app.BACKLOG_FREQUENCY)
            app.backlog_search_scheduler = BacklogSearchScheduler(BacklogSearcher(),
                                                                  cycleTime=update_interval,
                                                                  threadName='BACKLOG',
                                                                  run_delay=update_interval)

            if app.CHECK_PROPERS_INTERVAL in app.PROPERS_SEARCH_INTERVAL:
                update_interval = datetime.timedelta(minutes=app.PROPERS_SEARCH_INTERVAL[app.CHECK_PROPERS_INTERVAL])
                run_at = None
            else:
                update_interval = datetime.timedelta(hours=1)
                run_at = datetime.time(hour=1)  # 1 AM

            app.proper_finder_scheduler = scheduler.Scheduler(ProperFinder(),
                                                              cycleTime=update_interval,
                                                              threadName='FINDPROPERS',
                                                              start_time=run_at,
                                                              run_delay=update_interval)

            # processors
            update_interval = datetime.timedelta(minutes=app.AUTOPOSTPROCESSOR_FREQUENCY)
            app.auto_post_processor_scheduler = scheduler.Scheduler(auto_post_processor.PostProcessor(),
                                                                    cycleTime=update_interval,
                                                                    threadName='POSTPROCESSOR',
                                                                    silent=not app.PROCESS_AUTOMATICALLY,
                                                                    run_delay=update_interval)
            update_interval = datetime.timedelta(minutes=5)
            app.trakt_checker_scheduler = scheduler.Scheduler(trakt_checker.TraktChecker(),
                                                              cycleTime=datetime.timedelta(hours=1),
                                                              threadName='TRAKTCHECKER',
                                                              run_delay=update_interval,
                                                              silent=not app.USE_TRAKT)

            update_interval = datetime.timedelta(hours=app.SUBTITLES_FINDER_FREQUENCY)
            app.subtitles_finder_scheduler = scheduler.Scheduler(subtitles.SubtitlesFinder(),
                                                                 cycleTime=update_interval,
                                                                 threadName='FINDSUBTITLES',
                                                                 run_delay=update_interval,
                                                                 silent=not app.USE_SUBTITLES)

            update_interval = datetime.timedelta(minutes=app.TORRENT_CHECKER_FREQUENCY)
            app.torrent_checker_scheduler = scheduler.Scheduler(torrent_checker.TorrentChecker(),
                                                                cycleTime=update_interval,
                                                                threadName='TORRENTCHECKER',
                                                                run_delay=update_interval)

            app.__INITIALIZED__ = True
            return True