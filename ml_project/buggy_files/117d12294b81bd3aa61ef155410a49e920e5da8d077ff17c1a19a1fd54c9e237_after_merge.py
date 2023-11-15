    def save_settings(self):
        # Create a dictionary with all available settings
        settings_data = {'general': {}, 'Tribler': {}, 'downloadconfig': {}, 'libtorrent': {}, 'watch_folder': {},
                         'tunnel_community': {}, 'multichain': {}}
        settings_data['general']['family_filter'] = self.window().family_filter_checkbox.isChecked()
        settings_data['downloadconfig']['saveas'] = self.window().download_location_input.text().encode('utf-8')
        settings_data['general']['log_dir'] = self.window().log_location_input.text()

        settings_data['watch_folder']['enabled'] = self.window().watchfolder_enabled_checkbox.isChecked()
        if settings_data['watch_folder']['enabled']:
            settings_data['watch_folder']['watch_folder_dir'] = self.window().watchfolder_location_input.text()

        settings_data['general']['minport'] = self.window().firewall_current_port_input.text()
        settings_data['libtorrent']['lt_proxytype'] = self.window().lt_proxy_type_combobox.currentIndex()

        settings_data['libtorrent']['lt_proxyserver'] = None
        if self.window().lt_proxy_server_input.text() and len(self.window().lt_proxy_port_input.text()) > 0:
            settings_data['libtorrent']['lt_proxyserver'] = [self.window().lt_proxy_server_input.text(), None]

            # The port should be a number
            try:
                lt_proxy_port = int(self.window().lt_proxy_port_input.text())
                settings_data['libtorrent']['lt_proxyserver'][1] = lt_proxy_port
            except ValueError:
                ConfirmationDialog.show_error(self.window(), "Invalid proxy port number",
                                              "You've entered an invalid format for the proxy port number. "
                                              "Please enter a whole number.")
                return

        if len(self.window().lt_proxy_username_input.text()) > 0 and \
                        len(self.window().lt_proxy_password_input.text()) > 0:
            settings_data['libtorrent']['lt_proxyauth'] = [None, None]
            settings_data['libtorrent']['lt_proxyauth'][0] = self.window().lt_proxy_username_input.text()
            settings_data['libtorrent']['lt_proxyauth'][1] = self.window().lt_proxy_password_input.text()
        settings_data['libtorrent']['utp'] = self.window().lt_utp_checkbox.isChecked()

        try:
            max_conn_download = int(self.window().max_connections_download_input.text())
        except ValueError:
            ConfirmationDialog.show_error(self.window(), "Invalid number of connections",
                                          "You've entered an invalid format for the maximum number of connections. "
                                          "Please enter a whole number.")
            return
        if max_conn_download == 0:
            max_conn_download = -1
        settings_data['libtorrent']['max_connections_download'] = max_conn_download

        try:
            if self.window().upload_rate_limit_input.text():
                user_upload_rate_limit = int(self.window().upload_rate_limit_input.text()) * 1024
                if user_upload_rate_limit < sys.maxsize:
                    settings_data['libtorrent']['max_upload_rate'] = user_upload_rate_limit
                else:
                    raise ValueError
            if self.window().download_rate_limit_input.text():
                user_download_rate_limit = int(self.window().download_rate_limit_input.text()) * 1024
                if user_download_rate_limit < sys.maxsize:
                    settings_data['libtorrent']['max_download_rate'] = user_download_rate_limit
                else:
                    raise ValueError
        except ValueError:
            ConfirmationDialog.show_error(self.window(), "Invalid value for bandwidth limit",
                                          "You've entered an invalid value for the maximum upload/download rate. "
                                          "Please enter a whole number (max: %d)" % (sys.maxsize/1000))
            return

        seeding_modes = ['forever', 'time', 'never', 'ratio']
        selected_mode = 'forever'
        for seeding_mode in seeding_modes:
            if getattr(self.window(), "seeding_" + seeding_mode + "_radio").isChecked():
                selected_mode = seeding_mode
                break
        settings_data['downloadconfig']['seeding_mode'] = selected_mode
        settings_data['downloadconfig']['seeding_ratio'] = self.window().seeding_ratio_combobox.currentText()

        try:
            settings_data['downloadconfig']['seeding_time'] = string_to_seconds(self.window().seeding_time_input.text())
        except ValueError:
            ConfirmationDialog.show_error(self.window(), "Invalid seeding time",
                                          "You've entered an invalid format for the seeding time (expected HH:MM)")
            return

        settings_data['tunnel_community']['exitnode_enabled'] = self.window().allow_exit_node_checkbox.isChecked()
        settings_data['Tribler']['default_number_hops'] = self.window().number_hops_slider.value() + 1
        settings_data['multichain']['enabled'] = self.window().multichain_enabled_checkbox.isChecked()

        self.window().settings_save_button.setEnabled(False)

        self.settings_request_mgr = TriblerRequestManager()
        self.settings_request_mgr.perform_request("settings", self.on_settings_saved,
                                                  method='POST', data=json.dumps(settings_data))