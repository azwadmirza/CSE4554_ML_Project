    def __init__(self, common):
        super(SettingsDialog, self).__init__()

        self.common = common

        self.common.log("SettingsDialog", "__init__")

        self.setModal(True)
        self.setWindowTitle(strings._("gui_settings_window_title"))
        self.setWindowIcon(QtGui.QIcon(GuiCommon.get_resource_path("images/logo.png")))

        self.system = platform.system()

        # If ONIONSHARE_HIDE_TOR_SETTINGS=1, hide Tor settings in the dialog
        self.hide_tor_settings = os.environ.get("ONIONSHARE_HIDE_TOR_SETTINGS") == "1"

        # Automatic updates options

        # Autoupdate
        self.autoupdate_checkbox = QtWidgets.QCheckBox()
        self.autoupdate_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.autoupdate_checkbox.setText(strings._("gui_settings_autoupdate_option"))

        # Last update time
        self.autoupdate_timestamp = QtWidgets.QLabel()

        # Check for updates button
        self.check_for_updates_button = QtWidgets.QPushButton(
            strings._("gui_settings_autoupdate_check_button")
        )
        self.check_for_updates_button.clicked.connect(self.check_for_updates)
        # We can't check for updates if not connected to Tor
        if not self.common.gui.onion.connected_to_tor:
            self.check_for_updates_button.setEnabled(False)

        # Autoupdate options layout
        autoupdate_group_layout = QtWidgets.QVBoxLayout()
        autoupdate_group_layout.addWidget(self.autoupdate_checkbox)
        autoupdate_group_layout.addWidget(self.autoupdate_timestamp)
        autoupdate_group_layout.addWidget(self.check_for_updates_button)
        autoupdate_group = QtWidgets.QGroupBox(
            strings._("gui_settings_autoupdate_label")
        )
        autoupdate_group.setLayout(autoupdate_group_layout)

        # Autoupdate is only available for Windows and Mac (Linux updates using package manager)
        if self.system != "Windows" and self.system != "Darwin":
            autoupdate_group.hide()

        # Language settings
        language_label = QtWidgets.QLabel(strings._("gui_settings_language_label"))
        self.language_combobox = QtWidgets.QComboBox()
        # Populate the dropdown with all of OnionShare's available languages
        language_names_to_locales = {
            v: k for k, v in self.common.settings.available_locales.items()
        }
        language_names = list(language_names_to_locales)
        language_names.sort()
        for language_name in language_names:
            locale = language_names_to_locales[language_name]
            self.language_combobox.addItem(language_name, locale)
        language_layout = QtWidgets.QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        language_layout.addStretch()

        # Connection type: either automatic, control port, or socket file

        # Bundled Tor
        self.connection_type_bundled_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_connection_type_bundled_option")
        )
        self.connection_type_bundled_radio.toggled.connect(
            self.connection_type_bundled_toggled
        )

        # Bundled Tor doesn't work on dev mode in Windows or Mac
        if (self.system == "Windows" or self.system == "Darwin") and getattr(
            sys, "onionshare_dev_mode", False
        ):
            self.connection_type_bundled_radio.setEnabled(False)

        # Bridge options for bundled tor

        # No bridges option radio
        self.tor_bridges_no_bridges_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_tor_bridges_no_bridges_radio_option")
        )
        self.tor_bridges_no_bridges_radio.toggled.connect(
            self.tor_bridges_no_bridges_radio_toggled
        )

        # obfs4 option radio
        # if the obfs4proxy binary is missing, we can't use obfs4 transports
        (
            self.tor_path,
            self.tor_geo_ip_file_path,
            self.tor_geo_ipv6_file_path,
            self.obfs4proxy_file_path,
        ) = self.common.gui.get_tor_paths()
        if not self.obfs4proxy_file_path or not os.path.isfile(
            self.obfs4proxy_file_path
        ):
            self.tor_bridges_use_obfs4_radio = QtWidgets.QRadioButton(
                strings._("gui_settings_tor_bridges_obfs4_radio_option_no_obfs4proxy")
            )
            self.tor_bridges_use_obfs4_radio.setEnabled(False)
        else:
            self.tor_bridges_use_obfs4_radio = QtWidgets.QRadioButton(
                strings._("gui_settings_tor_bridges_obfs4_radio_option")
            )
        self.tor_bridges_use_obfs4_radio.toggled.connect(
            self.tor_bridges_use_obfs4_radio_toggled
        )

        # meek_lite-azure option radio
        # if the obfs4proxy binary is missing, we can't use meek_lite-azure transports
        (
            self.tor_path,
            self.tor_geo_ip_file_path,
            self.tor_geo_ipv6_file_path,
            self.obfs4proxy_file_path,
        ) = self.common.gui.get_tor_paths()
        if not self.obfs4proxy_file_path or not os.path.isfile(
            self.obfs4proxy_file_path
        ):
            self.tor_bridges_use_meek_lite_azure_radio = QtWidgets.QRadioButton(
                strings._(
                    "gui_settings_tor_bridges_meek_lite_azure_radio_option_no_obfs4proxy"
                )
            )
            self.tor_bridges_use_meek_lite_azure_radio.setEnabled(False)
        else:
            self.tor_bridges_use_meek_lite_azure_radio = QtWidgets.QRadioButton(
                strings._("gui_settings_tor_bridges_meek_lite_azure_radio_option")
            )
        self.tor_bridges_use_meek_lite_azure_radio.toggled.connect(
            self.tor_bridges_use_meek_lite_azure_radio_toggled
        )

        # Custom bridges radio and textbox
        self.tor_bridges_use_custom_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_tor_bridges_custom_radio_option")
        )
        self.tor_bridges_use_custom_radio.toggled.connect(
            self.tor_bridges_use_custom_radio_toggled
        )

        self.tor_bridges_use_custom_label = QtWidgets.QLabel(
            strings._("gui_settings_tor_bridges_custom_label")
        )
        self.tor_bridges_use_custom_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction
        )
        self.tor_bridges_use_custom_label.setOpenExternalLinks(True)
        self.tor_bridges_use_custom_textbox = QtWidgets.QPlainTextEdit()
        self.tor_bridges_use_custom_textbox.setMaximumHeight(200)
        self.tor_bridges_use_custom_textbox.setPlaceholderText(
            "[address:port] [identifier]"
        )

        tor_bridges_use_custom_textbox_options_layout = QtWidgets.QVBoxLayout()
        tor_bridges_use_custom_textbox_options_layout.addWidget(
            self.tor_bridges_use_custom_label
        )
        tor_bridges_use_custom_textbox_options_layout.addWidget(
            self.tor_bridges_use_custom_textbox
        )

        self.tor_bridges_use_custom_textbox_options = QtWidgets.QWidget()
        self.tor_bridges_use_custom_textbox_options.setLayout(
            tor_bridges_use_custom_textbox_options_layout
        )
        self.tor_bridges_use_custom_textbox_options.hide()

        # Bridges layout/widget
        bridges_layout = QtWidgets.QVBoxLayout()
        bridges_layout.addWidget(self.tor_bridges_no_bridges_radio)
        bridges_layout.addWidget(self.tor_bridges_use_obfs4_radio)
        bridges_layout.addWidget(self.tor_bridges_use_meek_lite_azure_radio)
        bridges_layout.addWidget(self.tor_bridges_use_custom_radio)
        bridges_layout.addWidget(self.tor_bridges_use_custom_textbox_options)

        self.bridges = QtWidgets.QWidget()
        self.bridges.setLayout(bridges_layout)

        # Automatic
        self.connection_type_automatic_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_connection_type_automatic_option")
        )
        self.connection_type_automatic_radio.toggled.connect(
            self.connection_type_automatic_toggled
        )

        # Control port
        self.connection_type_control_port_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_connection_type_control_port_option")
        )
        self.connection_type_control_port_radio.toggled.connect(
            self.connection_type_control_port_toggled
        )

        connection_type_control_port_extras_label = QtWidgets.QLabel(
            strings._("gui_settings_control_port_label")
        )
        self.connection_type_control_port_extras_address = QtWidgets.QLineEdit()
        self.connection_type_control_port_extras_port = QtWidgets.QLineEdit()
        connection_type_control_port_extras_layout = QtWidgets.QHBoxLayout()
        connection_type_control_port_extras_layout.addWidget(
            connection_type_control_port_extras_label
        )
        connection_type_control_port_extras_layout.addWidget(
            self.connection_type_control_port_extras_address
        )
        connection_type_control_port_extras_layout.addWidget(
            self.connection_type_control_port_extras_port
        )

        self.connection_type_control_port_extras = QtWidgets.QWidget()
        self.connection_type_control_port_extras.setLayout(
            connection_type_control_port_extras_layout
        )
        self.connection_type_control_port_extras.hide()

        # Socket file
        self.connection_type_socket_file_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_connection_type_socket_file_option")
        )
        self.connection_type_socket_file_radio.toggled.connect(
            self.connection_type_socket_file_toggled
        )

        connection_type_socket_file_extras_label = QtWidgets.QLabel(
            strings._("gui_settings_socket_file_label")
        )
        self.connection_type_socket_file_extras_path = QtWidgets.QLineEdit()
        connection_type_socket_file_extras_layout = QtWidgets.QHBoxLayout()
        connection_type_socket_file_extras_layout.addWidget(
            connection_type_socket_file_extras_label
        )
        connection_type_socket_file_extras_layout.addWidget(
            self.connection_type_socket_file_extras_path
        )

        self.connection_type_socket_file_extras = QtWidgets.QWidget()
        self.connection_type_socket_file_extras.setLayout(
            connection_type_socket_file_extras_layout
        )
        self.connection_type_socket_file_extras.hide()

        # Tor SOCKS address and port
        gui_settings_socks_label = QtWidgets.QLabel(
            strings._("gui_settings_socks_label")
        )
        self.connection_type_socks_address = QtWidgets.QLineEdit()
        self.connection_type_socks_port = QtWidgets.QLineEdit()
        connection_type_socks_layout = QtWidgets.QHBoxLayout()
        connection_type_socks_layout.addWidget(gui_settings_socks_label)
        connection_type_socks_layout.addWidget(self.connection_type_socks_address)
        connection_type_socks_layout.addWidget(self.connection_type_socks_port)

        self.connection_type_socks = QtWidgets.QWidget()
        self.connection_type_socks.setLayout(connection_type_socks_layout)
        self.connection_type_socks.hide()

        # Authentication options

        # No authentication
        self.authenticate_no_auth_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_authenticate_no_auth_option")
        )
        self.authenticate_no_auth_radio.toggled.connect(
            self.authenticate_no_auth_toggled
        )

        # Password
        self.authenticate_password_radio = QtWidgets.QRadioButton(
            strings._("gui_settings_authenticate_password_option")
        )
        self.authenticate_password_radio.toggled.connect(
            self.authenticate_password_toggled
        )

        authenticate_password_extras_label = QtWidgets.QLabel(
            strings._("gui_settings_password_label")
        )
        self.authenticate_password_extras_password = QtWidgets.QLineEdit("")
        authenticate_password_extras_layout = QtWidgets.QHBoxLayout()
        authenticate_password_extras_layout.addWidget(
            authenticate_password_extras_label
        )
        authenticate_password_extras_layout.addWidget(
            self.authenticate_password_extras_password
        )

        self.authenticate_password_extras = QtWidgets.QWidget()
        self.authenticate_password_extras.setLayout(authenticate_password_extras_layout)
        self.authenticate_password_extras.hide()

        # Authentication options layout
        authenticate_group_layout = QtWidgets.QVBoxLayout()
        authenticate_group_layout.addWidget(self.authenticate_no_auth_radio)
        authenticate_group_layout.addWidget(self.authenticate_password_radio)
        authenticate_group_layout.addWidget(self.authenticate_password_extras)
        self.authenticate_group = QtWidgets.QGroupBox(
            strings._("gui_settings_authenticate_label")
        )
        self.authenticate_group.setLayout(authenticate_group_layout)

        # Put the radios into their own group so they are exclusive
        connection_type_radio_group_layout = QtWidgets.QVBoxLayout()
        connection_type_radio_group_layout.addWidget(self.connection_type_bundled_radio)
        connection_type_radio_group_layout.addWidget(
            self.connection_type_automatic_radio
        )
        connection_type_radio_group_layout.addWidget(
            self.connection_type_control_port_radio
        )
        connection_type_radio_group_layout.addWidget(
            self.connection_type_socket_file_radio
        )
        connection_type_radio_group = QtWidgets.QGroupBox(
            strings._("gui_settings_connection_type_label")
        )
        connection_type_radio_group.setLayout(connection_type_radio_group_layout)

        # The Bridges options are not exclusive (enabling Bridges offers obfs4 or custom bridges)
        connection_type_bridges_radio_group_layout = QtWidgets.QVBoxLayout()
        connection_type_bridges_radio_group_layout.addWidget(self.bridges)
        self.connection_type_bridges_radio_group = QtWidgets.QGroupBox(
            strings._("gui_settings_tor_bridges")
        )
        self.connection_type_bridges_radio_group.setLayout(
            connection_type_bridges_radio_group_layout
        )
        self.connection_type_bridges_radio_group.hide()

        # Test tor settings button
        self.connection_type_test_button = QtWidgets.QPushButton(
            strings._("gui_settings_connection_type_test_button")
        )
        self.connection_type_test_button.clicked.connect(self.test_tor_clicked)
        connection_type_test_button_layout = QtWidgets.QHBoxLayout()
        connection_type_test_button_layout.addWidget(self.connection_type_test_button)
        connection_type_test_button_layout.addStretch()

        # Connection type layout
        connection_type_layout = QtWidgets.QVBoxLayout()
        connection_type_layout.addWidget(self.connection_type_control_port_extras)
        connection_type_layout.addWidget(self.connection_type_socket_file_extras)
        connection_type_layout.addWidget(self.connection_type_socks)
        connection_type_layout.addWidget(self.authenticate_group)
        connection_type_layout.addWidget(self.connection_type_bridges_radio_group)
        connection_type_layout.addLayout(connection_type_test_button_layout)

        # Buttons
        self.save_button = QtWidgets.QPushButton(strings._("gui_settings_button_save"))
        self.save_button.clicked.connect(self.save_clicked)
        self.cancel_button = QtWidgets.QPushButton(
            strings._("gui_settings_button_cancel")
        )
        self.cancel_button.clicked.connect(self.cancel_clicked)
        version_label = QtWidgets.QLabel(f"OnionShare {self.common.version}")
        version_label.setStyleSheet(self.common.gui.css["settings_version"])
        self.help_button = QtWidgets.QPushButton(strings._("gui_settings_button_help"))
        self.help_button.clicked.connect(self.help_clicked)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(version_label)
        buttons_layout.addWidget(self.help_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        # Tor network connection status
        self.tor_status = QtWidgets.QLabel()
        self.tor_status.setStyleSheet(self.common.gui.css["settings_tor_status"])
        self.tor_status.hide()

        # Layout
        tor_layout = QtWidgets.QVBoxLayout()
        tor_layout.addWidget(connection_type_radio_group)
        tor_layout.addLayout(connection_type_layout)
        tor_layout.addWidget(self.tor_status)
        tor_layout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        if not self.hide_tor_settings:
            layout.addLayout(tor_layout)
            layout.addSpacing(20)
        layout.addWidget(autoupdate_group)
        if autoupdate_group.isVisible():
            layout.addSpacing(20)
        layout.addLayout(language_layout)
        layout.addSpacing(20)
        layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.cancel_button.setFocus()

        self.reload_settings()