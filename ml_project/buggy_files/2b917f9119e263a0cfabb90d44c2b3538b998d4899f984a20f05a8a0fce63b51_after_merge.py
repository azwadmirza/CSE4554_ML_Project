    def __init__(self, common, onion, qtapp, app, filenames, config=False, local_only=False):
        super(OnionShareGui, self).__init__()

        self.common = common
        self.common.log('OnionShareGui', '__init__')
        self.setMinimumWidth(820)
        self.setMinimumHeight(660)

        self.onion = onion
        self.qtapp = qtapp
        self.app = app
        self.local_only = local_only

        self.mode = self.MODE_SHARE

        self.setWindowTitle('OnionShare')
        self.setWindowIcon(QtGui.QIcon(self.common.get_resource_path('images/logo.png')))

        # Load settings, if a custom config was passed in
        self.config = config
        if self.config:
            self.common.load_settings(self.config)
        else:
            self.common.load_settings()

        strings.load_strings(self.common)

        # System tray
        menu = QtWidgets.QMenu()
        self.settings_action = menu.addAction(strings._('gui_settings_window_title'))
        self.settings_action.triggered.connect(self.open_settings)
        self.help_action = menu.addAction(strings._('gui_settings_button_help'))
        self.help_action.triggered.connect(lambda: SettingsDialog.help_clicked(self))
        exit_action = menu.addAction(strings._('systray_menu_exit'))
        exit_action.triggered.connect(self.close)

        self.system_tray = QtWidgets.QSystemTrayIcon(self)
        # The convention is Mac systray icons are always grayscale
        if self.common.platform == 'Darwin':
            self.system_tray.setIcon(QtGui.QIcon(self.common.get_resource_path('images/logo_grayscale.png')))
        else:
            self.system_tray.setIcon(QtGui.QIcon(self.common.get_resource_path('images/logo.png')))
        self.system_tray.setContextMenu(menu)
        self.system_tray.show()

        # Mode switcher, to switch between share files and receive files
        self.share_mode_button = QtWidgets.QPushButton(strings._('gui_mode_share_button'));
        self.share_mode_button.setFixedHeight(50)
        self.share_mode_button.clicked.connect(self.share_mode_clicked)
        self.receive_mode_button = QtWidgets.QPushButton(strings._('gui_mode_receive_button'));
        self.receive_mode_button.setFixedHeight(50)
        self.receive_mode_button.clicked.connect(self.receive_mode_clicked)
        self.settings_button = QtWidgets.QPushButton()
        self.settings_button.setDefault(False)
        self.settings_button.setFixedWidth(40)
        self.settings_button.setFixedHeight(50)
        self.settings_button.setIcon( QtGui.QIcon(self.common.get_resource_path('images/settings.png')) )
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setStyleSheet(self.common.css['settings_button'])
        mode_switcher_layout = QtWidgets.QHBoxLayout();
        mode_switcher_layout.setSpacing(0)
        mode_switcher_layout.addWidget(self.share_mode_button)
        mode_switcher_layout.addWidget(self.receive_mode_button)
        mode_switcher_layout.addWidget(self.settings_button)

        # Server status indicator on the status bar
        self.server_status_image_stopped = QtGui.QImage(self.common.get_resource_path('images/server_stopped.png'))
        self.server_status_image_working = QtGui.QImage(self.common.get_resource_path('images/server_working.png'))
        self.server_status_image_started = QtGui.QImage(self.common.get_resource_path('images/server_started.png'))
        self.server_status_image_label = QtWidgets.QLabel()
        self.server_status_image_label.setFixedWidth(20)
        self.server_status_label = QtWidgets.QLabel('')
        self.server_status_label.setStyleSheet(self.common.css['server_status_indicator_label'])
        server_status_indicator_layout = QtWidgets.QHBoxLayout()
        server_status_indicator_layout.addWidget(self.server_status_image_label)
        server_status_indicator_layout.addWidget(self.server_status_label)
        self.server_status_indicator = QtWidgets.QWidget()
        self.server_status_indicator.setLayout(server_status_indicator_layout)

        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setStyleSheet(self.common.css['status_bar'])
        self.status_bar.addPermanentWidget(self.server_status_indicator)
        self.setStatusBar(self.status_bar)

        # Share mode
        self.share_mode = ShareMode(self.common, qtapp, app, self.status_bar, self.server_status_label, self.system_tray, filenames, self.local_only)
        self.share_mode.init()
        self.share_mode.server_status.server_started.connect(self.update_server_status_indicator)
        self.share_mode.server_status.server_stopped.connect(self.update_server_status_indicator)
        self.share_mode.start_server_finished.connect(self.update_server_status_indicator)
        self.share_mode.stop_server_finished.connect(self.update_server_status_indicator)
        self.share_mode.stop_server_finished.connect(self.stop_server_finished)
        self.share_mode.start_server_finished.connect(self.clear_message)
        self.share_mode.server_status.button_clicked.connect(self.clear_message)
        self.share_mode.server_status.url_copied.connect(self.copy_url)
        self.share_mode.server_status.hidservauth_copied.connect(self.copy_hidservauth)
        self.share_mode.set_server_active.connect(self.set_server_active)

        # Receive mode
        self.receive_mode = ReceiveMode(self.common, qtapp, app, self.status_bar, self.server_status_label, self.system_tray, None, self.local_only)
        self.receive_mode.init()
        self.receive_mode.server_status.server_started.connect(self.update_server_status_indicator)
        self.receive_mode.server_status.server_stopped.connect(self.update_server_status_indicator)
        self.receive_mode.start_server_finished.connect(self.update_server_status_indicator)
        self.receive_mode.stop_server_finished.connect(self.update_server_status_indicator)
        self.receive_mode.stop_server_finished.connect(self.stop_server_finished)
        self.receive_mode.start_server_finished.connect(self.clear_message)
        self.receive_mode.server_status.button_clicked.connect(self.clear_message)
        self.receive_mode.server_status.url_copied.connect(self.copy_url)
        self.receive_mode.server_status.hidservauth_copied.connect(self.copy_hidservauth)
        self.receive_mode.set_server_active.connect(self.set_server_active)

        self.update_mode_switcher()
        self.update_server_status_indicator()

        # Layouts
        contents_layout = QtWidgets.QVBoxLayout()
        contents_layout.setContentsMargins(10, 0, 10, 0)
        contents_layout.addWidget(self.receive_mode)
        contents_layout.addWidget(self.share_mode)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(mode_switcher_layout)
        layout.addLayout(contents_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.show()

        # The server isn't active yet
        self.set_server_active(False)

        # Create the timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_callback)

        # Start the "Connecting to Tor" dialog, which calls onion.connect()
        tor_con = TorConnectionDialog(self.common, self.qtapp, self.onion)
        tor_con.canceled.connect(self._tor_connection_canceled)
        tor_con.open_settings.connect(self._tor_connection_open_settings)
        if not self.local_only:
            tor_con.start()

        # Start the timer
        self.timer.start(500)

        # After connecting to Tor, check for updates
        self.check_for_updates()