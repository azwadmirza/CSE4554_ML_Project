    def _initSystemTray(self):
        menu = QtWidgets.QMenu()
        self.settingsAction = menu.addAction(strings._('gui_settings_window_title', True))
        self.settingsAction.triggered.connect(self.open_settings)
        self.helpAction = menu.addAction(strings._('gui_settings_button_help', True))
        self.helpAction.triggered.connect(SettingsDialog.help_clicked)
        self.exitAction = menu.addAction(strings._('systray_menu_exit', True))
        self.exitAction.triggered.connect(self.close)

        self.systemTray = QtWidgets.QSystemTrayIcon(self)
        # The convention is Mac systray icons are always grayscale
        if self.common.platform == 'Darwin':
            self.systemTray.setIcon(QtGui.QIcon(self.common.get_resource_path('images/logo_grayscale.png')))
        else:
            self.systemTray.setIcon(QtGui.QIcon(self.common.get_resource_path('images/logo.png')))
        self.systemTray.setContextMenu(menu)
        self.systemTray.show()