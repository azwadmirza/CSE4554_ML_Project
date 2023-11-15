    def on_start_download_action(self, action):
        if action == 1:
            if self.dialog and self.dialog.dialog_widget:
                self.window().perform_start_download_request(
                    self.download_uri, self.dialog.dialog_widget.anon_download_checkbox.isChecked(),
                    self.dialog.dialog_widget.safe_seed_checkbox.isChecked(),
                    self.dialog.dialog_widget.destination_input.currentText(),
                    self.dialog.get_selected_files(),
                    self.dialog.dialog_widget.files_list_view.topLevelItemCount())
            else:
                ConfirmationDialog.show_error(self, "Tribler UI Error", "Something went wrong. Please try again.")
                logging.exception("Error while trying to download. Either dialog or dialog.dialog_widget is None")

        self.dialog.request_mgr.cancel_request()  # To abort the torrent info request
        self.dialog.setParent(None)
        self.dialog = None
        self.start_download_dialog_active = False

        if action == 0:  # We do this after removing the dialog since process_uri_request is blocking
            self.process_uri_request()