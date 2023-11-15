    def __init__(self):
        QMainWindow.__init__(self)

        self.navigation_stack = []
        self.feedback_dialog_is_open = False
        self.tribler_started = False
        self.tribler_settings = None
        self.debug_window = None
        self.core_manager = CoreManager()
        self.pending_requests = {}
        self.pending_uri_requests = []
        self.download_uri = None
        self.dialog = None
        self.new_version_dialog = None
        self.start_download_dialog_active = False
        self.request_mgr = None
        self.search_request_mgr = None
        self.search_suggestion_mgr = None
        self.selected_torrent_files = []
        self.vlc_available = True
        self.has_search_results = False
        self.last_search_query = None
        self.last_search_time = None
        self.start_time = time.time()

        sys.excepthook = self.on_exception

        uic.loadUi(get_ui_file_path('mainwindow.ui'), self)
        TriblerRequestManager.window = self

        # Load dynamic widgets
        uic.loadUi(get_ui_file_path('torrent_channel_list_container.ui'), self.channel_page_container)
        self.channel_torrents_list = self.channel_page_container.items_list
        self.channel_torrents_detail_widget = self.channel_page_container.details_tab_widget
        self.channel_torrents_detail_widget.initialize_details_widget()
        self.channel_torrents_list.itemClicked.connect(self.channel_page.clicked_item)

        uic.loadUi(get_ui_file_path('torrent_channel_list_container.ui'), self.search_page_container)
        self.search_results_list = self.search_page_container.items_list
        self.search_torrents_detail_widget = self.search_page_container.details_tab_widget
        self.search_torrents_detail_widget.initialize_details_widget()
        self.search_results_list.itemClicked.connect(self.on_channel_item_click)
        self.search_results_list.itemClicked.connect(self.search_results_page.clicked_item)

        def on_state_update(new_state):
            self.loading_text_label.setText(new_state)

        self.core_manager.core_state_update.connect(on_state_update)

        self.magnet_handler = MagnetHandler(self.window)
        QDesktopServices.setUrlHandler("magnet", self.magnet_handler, "on_open_magnet_link")

        QCoreApplication.setOrganizationDomain("nl")
        QCoreApplication.setOrganizationName("TUDelft")
        QCoreApplication.setApplicationName("Tribler")
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        self.read_settings()

        self.debug_pane_shortcut = QShortcut(QKeySequence("Ctrl+d"), self)
        self.debug_pane_shortcut.activated.connect(self.clicked_menu_button_debug)

        # Remove the focus rect on OS X
        for widget in self.findChildren(QLineEdit) + self.findChildren(QListWidget) + self.findChildren(QTreeWidget):
            widget.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.menu_buttons = [self.left_menu_button_home, self.left_menu_button_search, self.left_menu_button_my_channel,
                             self.left_menu_button_subscriptions, self.left_menu_button_video_player,
                             self.left_menu_button_downloads, self.left_menu_button_discovered]

        self.video_player_page.initialize_player()
        self.search_results_page.initialize_search_results_page()
        self.settings_page.initialize_settings_page()
        self.subscribed_channels_page.initialize()
        self.edit_channel_page.initialize_edit_channel_page()
        self.downloads_page.initialize_downloads_page()
        self.home_page.initialize_home_page()
        self.loading_page.initialize_loading_page()
        self.discovering_page.initialize_discovering_page()
        self.discovered_page.initialize_discovered_page()
        self.trust_page.initialize_trust_page()

        self.stackedWidget.setCurrentIndex(PAGE_LOADING)

        # Create the system tray icon
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(QIcon(QPixmap(get_image_path('tribler.png'))))
            self.tray_icon.show()
        else:
            self.tray_icon = None

        self.hide_left_menu_playlist()
        self.left_menu_button_debug.setHidden(True)
        self.top_menu_button.setHidden(True)
        self.left_menu.setHidden(True)
        self.trust_button.setHidden(True)
        self.settings_button.setHidden(True)
        self.add_torrent_button.setHidden(True)
        self.top_search_bar.setHidden(True)

        # Set various icons
        self.top_menu_button.setIcon(QIcon(get_image_path('menu.png')))

        self.search_completion_model = QStringListModel()
        completer = QCompleter()
        completer.setModel(self.search_completion_model)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.item_delegate = QStyledItemDelegate()
        completer.popup().setItemDelegate(self.item_delegate)
        completer.popup().setStyleSheet("""
        QListView {
            background-color: #404040;
        }

        QListView::item {
            color: #D0D0D0;
            padding-top: 5px;
            padding-bottom: 5px;
        }

        QListView::item:hover {
            background-color: #707070;
        }
        """)
        self.top_search_bar.setCompleter(completer)

        # Toggle debug if developer mode is enabled
        self.window().left_menu_button_debug.setHidden(
            not get_gui_setting(self.gui_settings, "debug", False, is_bool=True))

        self.core_manager.start()

        self.core_manager.events_manager.received_search_result_channel.connect(
            self.search_results_page.received_search_result_channel)
        self.core_manager.events_manager.received_search_result_torrent.connect(
            self.search_results_page.received_search_result_torrent)
        self.core_manager.events_manager.torrent_finished.connect(self.on_torrent_finished)
        self.core_manager.events_manager.new_version_available.connect(self.on_new_version_available)
        self.core_manager.events_manager.tribler_started.connect(self.on_tribler_started)

        # Install signal handler for ctrl+c events
        def sigint_handler(*_):
            self.close_tribler()

        signal.signal(signal.SIGINT, sigint_handler)

        self.installEventFilter(self.video_player_page)

        self.show()