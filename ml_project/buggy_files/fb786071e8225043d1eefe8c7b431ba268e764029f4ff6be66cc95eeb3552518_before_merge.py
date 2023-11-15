    def __init__(self, parent):
        SpyderCompletionPlugin.__init__(self, parent)
        self.available_languages = []
        self.client = KiteClient(None)
        self.kite_process = None

        # Installation dialog
        self.installation_thread = KiteInstallationThread(self)
        self.installer = KiteInstallerDialog(
            parent,
            self.installation_thread)

        # Status widget
        statusbar = parent.statusBar()  # MainWindow status bar
        self.open_file_updated = False
        self.status_widget = KiteStatusWidget(None, statusbar, self)

        # Signals
        self.client.sig_client_started.connect(self.http_client_ready)
        self.client.sig_status_response_ready[str].connect(
            self.set_status)
        self.client.sig_status_response_ready[dict].connect(
            self.set_status)
        self.client.sig_response_ready.connect(
            functools.partial(self.sig_response_ready.emit,
                              self.COMPLETION_CLIENT_NAME))

        self.client.sig_response_ready.connect(self._kite_onboarding)
        self.client.sig_status_response_ready.connect(self._kite_onboarding)
        self.client.sig_onboarding_response_ready.connect(
            self._show_onboarding_file)

        self.installation_thread.sig_installation_status.connect(
            self.set_status)
        self.status_widget.sig_clicked.connect(
            self.show_installation_dialog)
        # self.main.sig_setup_finished.connect(self.mainwindow_setup_finished)

        # Config
        self.update_configuration()