    def __init__(self, params, installdir, autoload_discovery=True,
                 use_torrent_search=True, use_channel_search=True):
        super(ABCApp, self).__init__()
        assert not isInIOThread(), "isInIOThread() seems to not be working correctly"
        self._logger = logging.getLogger(self.__class__.__name__)

        self.params = params
        self.installdir = installdir

        self.state_dir = None
        self.error = None
        self.last_update = 0
        self.ready = False
        self.done = False
        self.frame = None
        self.upgrader = None
        self.i2i_server = None

        # DISPERSY will be set when available
        self.dispersy = None
        self.tunnel_community = None

        self.webUI = None
        self.utility = None

        # Stage 1 start
        session = self.InitStage1(installdir, autoload_discovery=autoload_discovery,
                                  use_torrent_search=use_torrent_search, use_channel_search=use_channel_search)

        try:
            self._logger.info('Client Starting Up.')
            self._logger.info("Tribler is using %s as working directory", self.installdir)

            # Stage 2: show the splash window and start the session

            self.utility = Utility(self.installdir, session.get_state_dir())

            if self.utility.read_config(u'saveas', u'downloadconfig'):
                DefaultDownloadStartupConfig.getInstance().set_dest_dir(self.utility.read_config(u'saveas', u'downloadconfig'))

            self.utility.set_app(self)
            self.utility.set_session(session)
            self.guiUtility = GUIUtility.getInstance(self.utility, self.params, self)
            GUIDBProducer.getInstance()

            # Broadcast that the initialisation is starting for the splash gauge and those who are interested
            self.utility.session.notifier.notify(NTFY_STARTUP_TICK, NTFY_CREATE, None, None)

            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_INSERT, None, 'Starting API')
            wx.Yield()

            self._logger.info('Tribler Version: %s Build: %s', version_id, commit_id)

            version_info = self.utility.read_config('version_info')
            if version_info.get('version_id', None) != version_id:
                # First run of a different version
                version_info['first_run'] = int(time())
                version_info['version_id'] = version_id
                self.utility.write_config('version_info', version_info)

            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_INSERT, None, 'Starting session and upgrading database (it may take a while)')
            wx.Yield()

            session.start()
            self.dispersy = session.lm.dispersy
            self.dispersy.attach_progress_handler(self.progressHandler)

            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_INSERT, None, 'Initializing Family Filter')
            wx.Yield()
            cat = session.lm.category

            state = self.utility.read_config('family_filter')
            if state in (1, 0):
                cat.set_family_filter(state == 1)
            else:
                self.utility.write_config('family_filter', 1)
                self.utility.flush_config()

                cat.set_family_filter(True)

            # Create global speed limits
            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_INSERT, None, 'Setting up speed limits')
            wx.Yield()

            # Counter to suppress some event from occurring
            self.ratestatecallbackcount = 0

            maxup = self.utility.read_config('maxuploadrate')
            maxdown = self.utility.read_config('maxdownloadrate')
            # set speed limits using LibtorrentMgr
            session.set_max_upload_speed(maxup)
            session.set_max_download_speed(maxdown)

            # Only allow updates to come in after we defined ratelimiter
            self.prevActiveDownloads = []
            session.set_download_states_callback(self.sesscb_states_callback)

            # Schedule task for checkpointing Session, to avoid hash checks after
            # crashes.
            self.register_task("checkpoint_loop", LoopingCall(self.guiservthread_checkpoint_timer))\
                .start(SESSION_CHECKPOINT_INTERVAL, now=False)

            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_INSERT, None, 'GUIUtility register')
            wx.Yield()
            self.guiUtility.register()

            self.frame = MainFrame(self, None, False)
            self.frame.SetIcon(wx.Icon(os.path.join(self.installdir, 'Tribler',
                                                    'Main', 'vwxGUI', 'images',
                                                    'tribler.ico'),
                                       wx.BITMAP_TYPE_ICO))

            # Arno, 2011-06-15: VLC 1.1.10 pops up separate win, don't have two.
            self.frame.videoframe = None

            if sys.platform == 'win32':
                wx.CallAfter(self.frame.top_bg.Refresh)
                wx.CallAfter(self.frame.top_bg.Layout)
            else:
                self.frame.top_bg.Layout()

            # Arno, 2007-05-03: wxWidgets 2.8.3.0 and earlier have the MIME-type for .bmp
            # files set to 'image/x-bmp' whereas 'image/bmp' is the official one.
            try:
                bmphand = None
                hands = wx.Image.GetHandlers()
                for hand in hands:
                    if hand.GetMimeType() == 'image/x-bmp':
                        bmphand = hand
                        break
                # wx.Image.AddHandler()
                if bmphand is not None:
                    bmphand.SetMimeType('image/bmp')
            except:
                # wx < 2.7 don't like wx.Image.GetHandlers()
                print_exc()

            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_DELETE, None, None)
            wx.Yield()
            self.frame.Show(True)
            self.register_task('free_space_check', LoopingCall(self.guiservthread_free_space_check))\
                .start(FREE_SPACE_CHECK_INTERVAL)

            self.webUI = None
            if self.utility.read_config('use_webui'):
                try:
                    from Tribler.Main.webUI.webUI import WebUI
                    self.webUI = WebUI.getInstance(self.guiUtility.library_manager,
                                                   self.guiUtility.torrentsearch_manager,
                                                   self.utility.read_config('webui_port'))
                    self.webUI.start()
                except Exception:
                    print_exc()

            self.emercoin_mgr = None
            try:
                from Tribler.Main.Emercoin.EmercoinMgr import EmercoinMgr
                self.emercoin_mgr = EmercoinMgr(self.utility)
            except Exception:
                print_exc()

            wx.CallAfter(self.PostInit2)

            # 08/02/10 Boudewijn: Working from home though console
            # doesn't allow me to press close.  The statement below
            # gracefully closes Tribler after 120 seconds.
            # wx.CallLater(120*1000, wx.GetApp().Exit)

            self.ready = True

        except Exception as e:
            session.notifier.notify(NTFY_STARTUP_TICK, NTFY_DELETE, None, None)
            self.onError(e)