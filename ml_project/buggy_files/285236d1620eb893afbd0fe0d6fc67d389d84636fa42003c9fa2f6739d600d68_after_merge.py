    def init(self):
        """
        Custom initialization for ReceiveMode.
        """
        # Create the Web object
        self.web = Web(self.common, True, 'receive')

        # Server status
        self.server_status.set_mode('receive')
        self.server_status.server_started_finished.connect(self.update_primary_action)
        self.server_status.server_stopped.connect(self.update_primary_action)
        self.server_status.server_canceled.connect(self.update_primary_action)

        # Tell server_status about web, then update
        self.server_status.web = self.web
        self.server_status.update()

        # Upload history
        self.history = History(
            self.common,
            QtGui.QPixmap.fromImage(QtGui.QImage(self.common.get_resource_path('images/receive_icon_transparent.png'))),
            strings._('gui_receive_mode_no_files'),
            strings._('gui_all_modes_history')
        )
        self.history.hide()

        # Toggle history
        self.toggle_history = ToggleHistory(
            self.common, self, self.history,
            QtGui.QIcon(self.common.get_resource_path('images/receive_icon_toggle.png')),
            QtGui.QIcon(self.common.get_resource_path('images/receive_icon_toggle_selected.png'))
        )

        # Receive mode warning
        receive_warning = QtWidgets.QLabel(strings._('gui_receive_mode_warning'))
        receive_warning.setMinimumHeight(80)
        receive_warning.setWordWrap(True)

        # Top bar
        top_bar_layout = QtWidgets.QHBoxLayout()
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.toggle_history)

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(top_bar_layout)
        self.main_layout.addWidget(receive_warning)
        self.main_layout.addWidget(self.primary_action)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.min_width_widget)

        # Wrapper layout
        self.wrapper_layout = QtWidgets.QHBoxLayout()
        self.wrapper_layout.addLayout(self.main_layout)
        self.wrapper_layout.addWidget(self.history, stretch=1)
        self.setLayout(self.wrapper_layout)