    def initialize_with_settings(self, settings):
        if not settings:
            return
        self.settings = settings
        settings = settings["settings"]
        gui_settings = self.window().gui_settings

        # General settings
        self.window().family_filter_checkbox.setChecked(settings['general']['family_filter'])
        self.window().use_monochrome_icon_checkbox.setChecked(get_gui_setting(gui_settings, "use_monochrome_icon",
                                                                              False, is_bool=True))
        self.window().download_location_input.setText(settings['download_defaults']['saveas'])
        self.window().always_ask_location_checkbox.setChecked(
            get_gui_setting(gui_settings, "ask_download_settings", True, is_bool=True))
        self.window().download_settings_anon_checkbox.setChecked(settings['download_defaults']['anonymity_enabled'])
        self.window().download_settings_anon_seeding_checkbox.setChecked(settings['download_defaults'][
                                                                             'safeseeding_enabled'])
        self.window().watchfolder_enabled_checkbox.setChecked(settings['watch_folder']['enabled'])
        self.window().watchfolder_location_input.setText(settings['watch_folder']['directory'])

        # Log directory
        self.window().log_location_input.setText(settings['general']['log_dir'])

        # Connection settings
        self.window().lt_proxy_type_combobox.setCurrentIndex(settings['libtorrent']['proxy_type'])
        if settings['libtorrent']['proxy_server']:
            self.window().lt_proxy_server_input.setText(settings['libtorrent']['proxy_server'][0])
            self.window().lt_proxy_port_input.setText("%s" % settings['libtorrent']['proxy_server'][1])
        if settings['libtorrent']['proxy_auth']:
            self.window().lt_proxy_username_input.setText(settings['libtorrent']['proxy_auth'][0])
            self.window().lt_proxy_password_input.setText(settings['libtorrent']['proxy_auth'][1])
        self.window().lt_utp_checkbox.setChecked(settings['libtorrent']['utp'])

        max_conn_download = settings['libtorrent']['max_connections_download']
        if max_conn_download == -1:
            max_conn_download = 0
        self.window().max_connections_download_input.setText(str(max_conn_download))

        self.window().api_port_input.setText("%s" % get_gui_setting(gui_settings, "api_port", DEFAULT_API_PORT))

        # Bandwidth settings
        self.window().upload_rate_limit_input.setText(str(settings['libtorrent']['max_upload_rate'] / 1024))
        self.window().download_rate_limit_input.setText(str(settings['libtorrent']['max_download_rate'] / 1024))

        # Seeding settings
        getattr(self.window(), "seeding_" + settings['download_defaults']['seeding_mode'] + "_radio").setChecked(True)
        self.window().seeding_time_input.setText(seconds_to_hhmm_string(settings['download_defaults']['seeding_time']))
        ind = self.window().seeding_ratio_combobox.findText(str(settings['download_defaults']['seeding_ratio']))
        if ind != -1:
            self.window().seeding_ratio_combobox.setCurrentIndex(ind)

        # Anonymity settings
        self.window().allow_exit_node_checkbox.setChecked(settings['tunnel_community']['exitnode_enabled'])
        self.window().number_hops_slider.setValue(int(settings['download_defaults']['number_hops']) - 1)
        self.window().credit_mining_enabled_checkbox.setChecked(settings['credit_mining']['enabled'])
        self.window().max_disk_space_input.setText(str(settings['credit_mining']['max_disk_space']))

        # Debug
        self.window().developer_mode_enabled_checkbox.setChecked(get_gui_setting(gui_settings, "debug",
                                                                                 False, is_bool=True))
        self.window().checkbox_enable_resource_log.setChecked(settings['resource_monitor']['enabled'])
        cpu_priority = 1
        if 'cpu_priority' in settings['resource_monitor']:
            cpu_priority = int(settings['resource_monitor']['cpu_priority'])
        self.window().slider_cpu_level.setValue(cpu_priority)
        self.window().cpu_priority_value.setText("Current Priority = %s" % cpu_priority)
        self.window().slider_cpu_level.valueChanged.connect(self.show_updated_cpu_priority)