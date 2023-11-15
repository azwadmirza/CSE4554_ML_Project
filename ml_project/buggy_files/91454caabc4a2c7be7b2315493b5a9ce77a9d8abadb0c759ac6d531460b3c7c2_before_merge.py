    def __init__(self, mode=None):

        # Create main window base class
        QMainWindow.__init__(self)
        self.mode = mode    # None or unittest (None is normal usage)
        self.initialized = False

        # set window on app for reference during initialization of children
        app = get_app()
        app.window = self
        _ = app._tr

        # Load user settings for window
        s = settings.get_settings()
        self.recent_menu = None

        # Track metrics
        track_metric_session()  # start session

        # Set unique install id (if blank)
        if not s.get("unique_install_id"):
            s.set("unique_install_id", str(uuid4()))

            # Track 1st launch metric
            track_metric_screen("initial-launch-screen")

        # Track main screen
        track_metric_screen("main-screen")

        # Create blank tutorial manager
        self.tutorial_manager = None

        # Load UI from designer
        ui_util.load_ui(self, self.ui_path)

        # Set all keyboard shortcuts from the settings file
        self.InitKeyboardShortcuts()

        # Init UI
        ui_util.init_ui(self)

        # Setup toolbars that aren't on main window, set initial state of items, etc
        self.setup_toolbars()

        # Add window as watcher to receive undo/redo status updates
        app.updates.add_watcher(self)

        # Get current version of OpenShot via HTTP
        self.FoundVersionSignal.connect(self.foundCurrentVersion)
        get_current_Version()

        # Connect signals
        if self.mode != "unittest":
            self.RecoverBackup.connect(self.recover_backup)

        # Initialize and start the thumbnail HTTP server
        self.http_server_thread = httpThumbnailServerThread()
        self.http_server_thread.start()

        # Create the timeline sync object (used for previewing timeline)
        self.timeline_sync = TimelineSync(self)

        # Setup timeline
        self.timeline = TimelineWebView(self)
        self.frameWeb.layout().addWidget(self.timeline)

        # Configure the side docks to full-height
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # Setup files tree and list view (both share a model)
        self.files_model = FilesModel()
        self.filesTreeView = FilesTreeView(self.files_model)
        self.filesListView = FilesListView(self.files_model)
        self.files_model.update_model()
        self.tabFiles.layout().insertWidget(-1, self.filesTreeView)
        self.tabFiles.layout().insertWidget(-1, self.filesListView)
        if s.get("file_view") == "details":
            self.filesView = self.filesTreeView
            self.filesListView.hide()
        else:
            self.filesView = self.filesListView
            self.filesTreeView.hide()
        # Show our currently-enabled project files view
        self.filesView.show()
        self.filesView.setFocus()

        # Setup transitions tree and list views
        self.transition_model = TransitionsModel()
        self.transitionsTreeView = TransitionsTreeView(self.transition_model)
        self.transitionsListView = TransitionsListView(self.transition_model)
        self.transition_model.update_model()
        self.tabTransitions.layout().insertWidget(-1, self.transitionsTreeView)
        self.tabTransitions.layout().insertWidget(-1, self.transitionsListView)
        if s.get("transitions_view") == "details":
            self.transitionsView = self.transitionsTreeView
            self.transitionsListView.hide()
        else:
            self.transitionsView = self.transitionsListView
            self.transitionsTreeView.hide()
        # Show our currently-enabled transitions view
        self.transitionsView.show()
        self.transitionsView.setFocus()

        # Setup effects tree
        self.effects_model = EffectsModel()
        self.effectsTreeView = EffectsTreeView(self.effects_model)
        self.effectsListView = EffectsListView(self.effects_model)
        self.effects_model.update_model()
        self.tabEffects.layout().insertWidget(-1, self.effectsTreeView)
        self.tabEffects.layout().insertWidget(-1, self.effectsListView)
        if s.get("effects_view") == "details":
            self.effectsView = self.effectsTreeView
            self.effectsListView.hide()
        else:
            self.effectsView = self.effectsListView
            self.effectsTreeView.hide()
        # Show our currently-enabled effects view
        self.effectsView.show()
        self.effectsView.setFocus()

        # Setup emojis view
        self.emojis_model = EmojisModel()
        self.emojis_model.update_model()
        self.emojiListView = EmojisListView(self.emojis_model)
        self.tabEmojis.layout().addWidget(self.emojiListView)

        # Add Docks submenu to View menu
        self.addViewDocksMenu()

        # Set up status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Process events before continuing
        # TODO: Figure out why this is needed for a backup recovery to correctly show up on the timeline
        app.processEvents()

        # Setup properties table
        self.txtPropertyFilter.setPlaceholderText(_("Filter"))
        self.propertyTableView = PropertiesTableView(self)
        self.selectionLabel = SelectionLabel(self)
        self.dockPropertiesContent.layout().addWidget(self.selectionLabel, 0, 1)
        self.dockPropertiesContent.layout().addWidget(self.propertyTableView, 2, 1)

        # Init selection containers
        self.clearSelections()

        # Show Property timer
        # Timer to use a delay before showing properties (to prevent a mass selection from trying
        # to update the property model hundreds of times)
        self.show_property_id = None
        self.show_property_type = None
        self.show_property_timer = QTimer()
        self.show_property_timer.setInterval(100)
        self.show_property_timer.setSingleShot(True)
        self.show_property_timer.timeout.connect(self.show_property_timeout)

        # Setup video preview QWidget
        self.videoPreview = VideoWidget()
        self.tabVideo.layout().insertWidget(0, self.videoPreview)

        # Load window state and geometry
        self.load_settings()

        # Setup Cache settings
        self.cache_object = None
        self.InitCacheSettings()

        # Start the preview thread
        self.preview_parent = PreviewParent()
        self.preview_parent.Init(self, self.timeline_sync.timeline, self.videoPreview)
        self.preview_thread = self.preview_parent.worker

        # Set pause callback
        self.PauseSignal.connect(self.handlePausedVideo)

        # QTimer for Autosave
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setInterval(int(s.get("autosave-interval") * 1000 * 60))
        self.auto_save_timer.timeout.connect(self.auto_save_project)
        if s.get("enable-auto-save"):
            self.auto_save_timer.start()

        # Set encoding method
        if s.get("hw-decoder"):
            openshot.Settings.Instance().HARDWARE_DECODER = int(str(s.get("hw-decoder")))
        else:
            openshot.Settings.Instance().HARDWARE_DECODER = 0

        # Set graphics card for decoding
        if s.get("graca_number_de"):
            if int(str(s.get("graca_number_de"))) != 0:
                openshot.Settings.Instance().HW_DE_DEVICE_SET = int(str(s.get("graca_number_de")))
            else:
                openshot.Settings.Instance().HW_DE_DEVICE_SET = 0
        else:
            openshot.Settings.Instance().HW_DE_DEVICE_SET = 0

        # Set graphics card for encoding
        if s.get("graca_number_en"):
            if int(str(s.get("graca_number_en"))) != 0:
                openshot.Settings.Instance().HW_EN_DEVICE_SET = int(str(s.get("graca_number_en")))
            else:
                openshot.Settings.Instance().HW_EN_DEVICE_SET = 0
        else:
            openshot.Settings.Instance().HW_EN_DEVICE_SET = 0

        # Set audio playback settings
        if s.get("playback-audio-device"):
            openshot.Settings.Instance().PLAYBACK_AUDIO_DEVICE_NAME = str(s.get("playback-audio-device"))
        else:
            openshot.Settings.Instance().PLAYBACK_AUDIO_DEVICE_NAME = ""

        # Set OMP thread enabled flag (for stability)
        if s.get("omp_threads_enabled"):
            openshot.Settings.Instance().WAIT_FOR_VIDEO_PROCESSING_TASK = False
        else:
            openshot.Settings.Instance().WAIT_FOR_VIDEO_PROCESSING_TASK = True

        # Set scaling mode to lower quality scaling (for faster previews)
        openshot.Settings.Instance().HIGH_QUALITY_SCALING = False

        # Set use omp threads number environment variable
        if s.get("omp_threads_number"):
            openshot.Settings.Instance().OMP_THREADS = max(2, int(str(s.get("omp_threads_number"))))
        else:
            openshot.Settings.Instance().OMP_THREADS = 12

        # Set use ffmpeg threads number environment variable
        if s.get("ff_threads_number"):
            openshot.Settings.Instance().FF_THREADS = max(1, int(str(s.get("ff_threads_number"))))
        else:
            openshot.Settings.Instance().FF_THREADS = 8

        # Set use max width decode hw environment variable
        if s.get("decode_hw_max_width"):
            openshot.Settings.Instance().DE_LIMIT_WIDTH_MAX = int(str(s.get("decode_hw_max_width")))

        # Set use max height decode hw environment variable
        if s.get("decode_hw_max_height"):
            openshot.Settings.Instance().DE_LIMIT_HEIGHT_MAX = int(str(s.get("decode_hw_max_height")))

        # Create lock file
        self.create_lock_file()

        # Connect OpenProject Signal
        self.OpenProjectSignal.connect(self.open_project)

        # Show window
        if self.mode != "unittest":
            self.show()
        else:
            log.info('Hiding UI for unittests')

        # Create tutorial manager
        self.tutorial_manager = TutorialManager(self)

        # Connect to Unity DBus signal (if linux)
        self.unity_launcher = None
        if "linux" in sys.platform:
            try:
                # Get connection to Unity Launcher
                import gi
                gi.require_version('Unity', '7.0')
                from gi.repository import Unity
                self.unity_launcher = Unity.LauncherEntry.get_for_desktop_id(info.DESKTOP_ID)
            except Exception:
                log.debug('Failed to connect to Unity launcher (Linux only) for updating export progress.')
            else:
                self.ExportFrame.connect(self.FrameExported)
                self.ExportEnded.connect(self.ExportFinished)

        # Save settings
        s.save()

        # Refresh frame
        QTimer.singleShot(100, self.refreshFrameSignal.emit)

        # Main window is initialized
        self.initialized = True