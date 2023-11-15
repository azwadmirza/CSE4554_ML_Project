    def on_confirm_add_directory_dialog(self, action):
        if action == 0:
            if self.dialog.checkbox.isChecked():
                self.add_dir_to_channel(self.chosen_dir, callback=self.on_dir_added_to_channel)
            for torrent_file in self.selected_torrent_files:
                escaped_uri = u"file:%s" % pathname2url(torrent_file.encode('utf-8'))
                self.perform_start_download_request(escaped_uri,
                                                    self.window().tribler_settings['download_defaults'][
                                                        'anonymity_enabled'],
                                                    self.window().tribler_settings['download_defaults'][
                                                        'safeseeding_enabled'],
                                                    self.tribler_settings['download_defaults']['saveas'], [], 0)

        if self.dialog:
            self.dialog.close_dialog()
            self.dialog = None