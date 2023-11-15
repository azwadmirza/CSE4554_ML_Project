    def save_settings(self):
        # Create a dictionary with all available settings
        settings_data = {
            'general': {},
            'Tribler': {},
            'download_defaults': {},
            'libtorrent': {},
            'watch_folder': {},
            'tunnel_community': {},
            'market_community': {},
            'trustchain': {},
            'resource_monitor': {},
            'ipv8': {},
            'chant': {},
        }
        settings_data['download_defaults']['saveas'] = self.window().download_location_input.text()
        settings_data['general']['log_dir'] = self.window().log_location_input.text()

        settings_data['watch_folder']['enabled'] = self.window().watchfolder_enabled_checkbox.isChecked()
        if settings_data['watch_folder']['enabled']:
            settings_data['watch_folder']['directory'] = self.window().watchfolder_location_input.text()

        settings_data['market_community']['enabled'] = self.window().enable_market_checkbox.isChecked()

        settings_data['libtorrent']['proxy_type'] = self.window().lt_proxy_type_combobox.currentIndex()

        if (
            self.window().lt_proxy_server_input.text()
            and len(self.window().lt_proxy_server_input.text()) > 0
            and len(self.window().lt_proxy_port_input.text()) > 0
        ):
            try:
                settings_data['libtorrent']['proxy_server'] = "%s:%s" % (
                    self.window().lt_proxy_server_input.text(),
                    int(self.window().lt_proxy_port_input.text()),
                )
            except ValueError:
                ConfirmationDialog.show_error(
                    self.window(),
                    "Invalid proxy port number",
                    "You've entered an invalid format for the proxy port number. " "Please enter a whole number.",
                )
                return
        else:
            settings_data['libtorrent']['proxy_server'] = ":"

        if self.window().lt_proxy_username_input.text() and self.window().lt_proxy_password_input.text():
            settings_data['libtorrent']['proxy_auth'] = "%s:%s" % (
                self.window().lt_proxy_username_input.text(),
                self.window().lt_proxy_password_input.text(),
            )
        else:
            settings_data['libtorrent']['proxy_auth'] = ":"

        settings_data['libtorrent']['utp'] = self.window().lt_utp_checkbox.isChecked()

        try:
            max_conn_download = int(self.window().max_connections_download_input.text())
        except ValueError:
            ConfirmationDialog.show_error(
                self.window(),
                "Invalid number of connections",
                "You've entered an invalid format for the maximum number of connections. "
                "Please enter a whole number.",
            )
            return
        if max_conn_download == 0:
            max_conn_download = -1
        settings_data['libtorrent']['max_connections_download'] = max_conn_download

        try:
            if self.window().upload_rate_limit_input.text():
                user_upload_rate_limit = int(float(self.window().upload_rate_limit_input.text()) * 1024)
                if user_upload_rate_limit < MAX_LIBTORRENT_RATE_LIMIT:
                    settings_data['libtorrent']['max_upload_rate'] = user_upload_rate_limit
                else:
                    raise ValueError
            if self.window().download_rate_limit_input.text():
                user_download_rate_limit = int(float(self.window().download_rate_limit_input.text()) * 1024)
                if user_download_rate_limit < MAX_LIBTORRENT_RATE_LIMIT:
                    settings_data['libtorrent']['max_download_rate'] = user_download_rate_limit
                else:
                    raise ValueError
        except ValueError:
            ConfirmationDialog.show_error(
                self.window(),
                "Invalid value for bandwidth limit",
                "You've entered an invalid value for the maximum upload/download rate. \n"
                "The rate is specified in KB/s and the value permitted is between 0 and %d KB/s.\n"
                "Note that the decimal values are truncated." % (MAX_LIBTORRENT_RATE_LIMIT / 1024),
            )
            return

        try:
            if self.window().api_port_input.text():
                api_port = int(self.window().api_port_input.text())
                if api_port <= 0 or api_port >= 65536:
                    raise ValueError()
                self.window().gui_settings.setValue("api_port", api_port)
        except ValueError:
            ConfirmationDialog.show_error(
                self.window(),
                "Invalid value for api port",
                "Please enter a valid port for the api (between 0 and 65536)",
            )
            return

        seeding_modes = ['forever', 'time', 'never', 'ratio']
        selected_mode = 'forever'
        for seeding_mode in seeding_modes:
            if getattr(self.window(), "seeding_" + seeding_mode + "_radio").isChecked():
                selected_mode = seeding_mode
                break
        settings_data['download_defaults']['seeding_mode'] = selected_mode
        settings_data['download_defaults']['seeding_ratio'] = float(self.window().seeding_ratio_combobox.currentText())

        try:
            settings_data['download_defaults']['seeding_time'] = string_to_seconds(
                self.window().seeding_time_input.text()
            )
        except ValueError:
            ConfirmationDialog.show_error(
                self.window(),
                "Invalid seeding time",
                "You've entered an invalid format for the seeding time (expected HH:MM)",
            )
            return

        settings_data['tunnel_community']['exitnode_enabled'] = self.window().allow_exit_node_checkbox.isChecked()
        settings_data['download_defaults']['number_hops'] = self.window().number_hops_slider.value()
        settings_data['download_defaults'][
            'anonymity_enabled'
        ] = self.window().download_settings_anon_checkbox.isChecked()
        settings_data['download_defaults'][
            'safeseeding_enabled'
        ] = self.window().download_settings_anon_seeding_checkbox.isChecked()
        settings_data['download_defaults'][
            'add_download_to_channel'
        ] = self.window().download_settings_add_to_channel_checkbox.isChecked()

        settings_data['resource_monitor']['enabled'] = self.window().checkbox_enable_resource_log.isChecked()
        settings_data['resource_monitor']['cpu_priority'] = int(self.window().slider_cpu_level.value())

        # network statistics
        settings_data['ipv8']['statistics'] = self.window().checkbox_enable_network_statistics.isChecked()

        self.window().settings_save_button.setEnabled(False)

        # TODO: do it in RESTful style, on the REST return JSON instead
        # In case the default save dir has changed, add it to the top of the list of last download locations.
        # Otherwise, the user could absentmindedly click through the download dialog and start downloading into
        # the last used download dir, and not into the newly designated default download dir.
        if self.settings['download_defaults']['saveas'] != settings_data['download_defaults']['saveas']:
            self.window().update_recent_download_locations(settings_data['download_defaults']['saveas'])
        self.settings = settings_data

        TriblerNetworkRequest("settings", self.on_settings_saved, method='POST', raw_data=json.dumps(settings_data))