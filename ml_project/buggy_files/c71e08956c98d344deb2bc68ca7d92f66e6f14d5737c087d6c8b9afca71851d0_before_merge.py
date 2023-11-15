    def received_settings(self, settings):
        # If we cannot receive the settings, stop Tribler with an option to send the crash report.
        if 'error' in settings:
            raise RuntimeError(TriblerRequestManager.get_message_from_error(settings))

        self.tribler_settings = settings['settings']

        # Set the video server port
        self.video_player_page.video_player_port = settings["ports"]["video_server~port"]

        # Disable various components based on the settings
        if not self.tribler_settings['search_community']['enabled']:
            self.window().top_search_bar.setHidden(True)
        if not self.tribler_settings['video_server']['enabled']:
            self.left_menu_button_video_player.setHidden(True)
        self.downloads_creditmining_button.setHidden(not self.tribler_settings["credit_mining"]["enabled"])
        self.downloads_all_button.click()

        # process pending file requests (i.e. someone clicked a torrent file when Tribler was closed)
        # We do this after receiving the settings so we have the default download location.
        self.process_uri_request()

        # Set token balance refresh timer and load the token balance
        self.token_refresh_timer = QTimer()
        self.token_refresh_timer.timeout.connect(self.load_token_balance)
        self.token_refresh_timer.start(60000)

        self.load_token_balance()