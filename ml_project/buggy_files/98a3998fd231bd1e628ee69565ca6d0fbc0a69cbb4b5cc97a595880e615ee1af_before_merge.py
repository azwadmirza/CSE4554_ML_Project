    def __init__(self, core_args=None, core_env=None, api_port=None, api_key=None):
        QMainWindow.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)

        QCoreApplication.setOrganizationDomain("nl")
        QCoreApplication.setOrganizationName("TUDelft")
        QCoreApplication.setApplicationName("Tribler")

        self.setWindowIcon(QIcon(QPixmap(get_image_path('tribler.png'))))

        self.gui_settings = QSettings()
        api_port = api_port or int(get_gui_setting(self.gui_settings, "api_port", DEFAULT_API_PORT))
        api_key = api_key or get_gui_setting(self.gui_settings, "api_key", hexlify(os.urandom(16)).encode('utf-8'))
        self.gui_settings.setValue("api_key", api_key)
        request_manager.port, request_manager.key = api_port, api_key

        self.tribler_started = False
        self.tribler_settings = None
        # TODO: move version_id to tribler_common and get core version in the core crash message
        self.tribler_version = version_id
        self.debug_window = None

        self.error_handler = ErrorHandler(self)
        self.core_manager = CoreManager(api_port, api_key, self.error_handler)
        self.pending_requests = {}
        self.pending_uri_requests = []
        self.download_uri = None
        self.dialog = None
        self.create_dialog = None
        self.chosen_dir = None
        self.new_version_dialog = None
        self.start_download_dialog_active = False
        self.selected_torrent_files = []
        self.has_search_results = False
        self.last_search_query = None
        self.last_search_time = None
        self.start_time = time.time()
        self.token_refresh_timer = None
        self.shutdown_timer = None
        self.add_torrent_url_dialog_active = False

        sys.excepthook = self.error_handler.gui_error

        uic.loadUi(get_ui_file_path('mainwindow.ui'), self)
        TriblerRequestManager.window = self
        self.tribler_status_bar.hide()

        self.token_balance_widget.mouseReleaseEvent = self.on_token_balance_click

        def on_state_update(new_state):
            self.loading_text_label.setText(new_state)

        connect(self.core_manager.core_state_update, on_state_update)

        self.magnet_handler = MagnetHandler(self.window)
        QDesktopServices.setUrlHandler("magnet", self.magnet_handler, "on_open_magnet_link")

        self.debug_pane_shortcut = QShortcut(QKeySequence("Ctrl+d"), self)
        connect(self.debug_pane_shortcut.activated, self.clicked_menu_button_debug)
        self.import_torrent_shortcut = QShortcut(QKeySequence("Ctrl+o"), self)
        connect(self.import_torrent_shortcut.activated, self.on_add_torrent_browse_file)
        self.add_torrent_url_shortcut = QShortcut(QKeySequence("Ctrl+i"), self)
        connect(self.add_torrent_url_shortcut.activated, self.on_add_torrent_from_url)

        connect(self.top_search_bar.clicked, self.clicked_search_bar)

        # Remove the focus rect on OS X
        for widget in self.findChildren(QLineEdit) + self.findChildren(QListWidget) + self.findChildren(QTreeWidget):
            widget.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.menu_buttons = [
            self.left_menu_button_downloads,
            self.left_menu_button_discovered,
            self.left_menu_button_trust_graph,
            self.left_menu_button_popular,
        ]
        hide_xxx = get_gui_setting(self.gui_settings, "family_filter", True, is_bool=True)
        self.search_results_page.initialize_content_page(hide_xxx=hide_xxx)
        self.search_results_page.channel_torrents_filter_input.setHidden(True)

        self.settings_page.initialize_settings_page()
        self.downloads_page.initialize_downloads_page()
        self.loading_page.initialize_loading_page()
        self.discovering_page.initialize_discovering_page()

        self.discovered_page.initialize_content_page(hide_xxx=hide_xxx)

        self.popular_page.initialize_content_page(hide_xxx=hide_xxx)

        self.trust_page.initialize_trust_page()
        self.trust_graph_page.initialize_trust_graph()

        self.stackedWidget.setCurrentIndex(PAGE_LOADING)

        # Create the system tray icon
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()
            use_monochrome_icon = get_gui_setting(self.gui_settings, "use_monochrome_icon", False, is_bool=True)
            self.update_tray_icon(use_monochrome_icon)

            # Create the tray icon menu
            menu = self.create_add_torrent_menu()
            show_downloads_action = QAction('Show downloads', self)
            connect(show_downloads_action.triggered, self.clicked_menu_button_downloads)
            token_balance_action = QAction('Show token balance', self)
            connect(token_balance_action.triggered, lambda _: self.on_token_balance_click(None))
            quit_action = QAction('Quit Tribler', self)
            connect(quit_action.triggered, self.close_tribler)
            menu.addSeparator()
            menu.addAction(show_downloads_action)
            menu.addAction(token_balance_action)
            menu.addSeparator()
            menu.addAction(quit_action)
            self.tray_icon.setContextMenu(menu)
        else:
            self.tray_icon = None

        self.left_menu_button_debug.setHidden(True)
        self.top_menu_button.setHidden(True)
        self.left_menu.setHidden(True)
        self.token_balance_widget.setHidden(True)
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
        completer.popup().setStyleSheet(
            """
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
        """
        )
        self.top_search_bar.setCompleter(completer)

        # Toggle debug if developer mode is enabled
        self.window().left_menu_button_debug.setHidden(
            not get_gui_setting(self.gui_settings, "debug", False, is_bool=True)
        )

        # Start Tribler
        self.core_manager.start(core_args=core_args, core_env=core_env)

        connect(self.core_manager.events_manager.torrent_finished, self.on_torrent_finished)
        connect(self.core_manager.events_manager.new_version_available, self.on_new_version_available)
        connect(self.core_manager.events_manager.tribler_started, self.on_tribler_started)
        connect(self.core_manager.events_manager.low_storage_signal, self.on_low_storage)
        connect(self.core_manager.events_manager.tribler_shutdown_signal, self.on_tribler_shutdown_state_update)
        connect(self.core_manager.events_manager.config_error_signal, self.on_config_error_signal)

        # Install signal handler for ctrl+c events
        def sigint_handler(*_):
            self.close_tribler()

        signal.signal(signal.SIGINT, sigint_handler)

        # Resize the window according to the settings
        center = QApplication.desktop().availableGeometry(self).center()
        pos = self.gui_settings.value("pos", QPoint(center.x() - self.width() * 0.5, center.y() - self.height() * 0.5))
        size = self.gui_settings.value("size", self.size())

        self.move(pos)
        self.resize(size)

        self.show()

        self.add_to_channel_dialog = AddToChannelDialog(self.window())

        self.add_torrent_menu = self.create_add_torrent_menu()
        self.add_torrent_button.setMenu(self.add_torrent_menu)

        self.channels_menu_list = self.findChild(ChannelsMenuListWidget, "channels_menu_list")

        connect(self.channels_menu_list.itemClicked, self.open_channel_contents_page)

        # The channels content page is only used to show subscribed channels, so we always show xxx
        # contents in it.
        connect(
            self.core_manager.events_manager.node_info_updated,
            lambda data: self.channels_menu_list.reload_if_necessary([data]),
        )
        connect(self.left_menu_button_new_channel.clicked, self.create_new_channel)