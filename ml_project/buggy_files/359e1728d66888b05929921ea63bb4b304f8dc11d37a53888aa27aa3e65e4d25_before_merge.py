    def on_start_download_action(self, action):
        if action == 1:
            self.window().perform_start_download_request(self.download_uri,
                                                         self.dialog.dialog_widget.anon_download_checkbox.isChecked(),
                                                         self.dialog.dialog_widget.safe_seed_checkbox.isChecked(),
                                                         self.dialog.dialog_widget.destination_input.currentText(),
                                                         self.dialog.get_selected_files(),
                                                         self.dialog.dialog_widget.files_list_view.topLevelItemCount())

        self.dialog.request_mgr.cancel_request()  # To abort the torrent info request
        self.dialog.setParent(None)
        self.dialog = None
        self.start_download_dialog_active = False

        if action == 0:  # We do this after removing the dialog since process_uri_request is blocking
            self.process_uri_request()