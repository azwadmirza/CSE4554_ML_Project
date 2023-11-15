    def on_export_download(self):
        self.export_dir = QFileDialog.getExistingDirectory(self, "Please select the destination directory", "",
                                                           QFileDialog.ShowDirsOnly)

        if len(self.export_dir) > 0:
            # Show confirmation dialog where we specify the name of the file
            infohash = self.selected_item.download_info['infohash']
            self.dialog = ConfirmationDialog(self, "Export torrent file",
                                             "Please enter the name of the torrent file:",
                                             [('SAVE', BUTTON_TYPE_NORMAL), ('CANCEL', BUTTON_TYPE_CONFIRM)],
                                             show_input=True)
            self.dialog.dialog_widget.dialog_input.setPlaceholderText('Torrent file name')
            self.dialog.dialog_widget.dialog_input.setText("%s.torrent" % infohash)
            self.dialog.dialog_widget.dialog_input.setFocus()
            self.dialog.button_clicked.connect(self.on_export_download_dialog_done)
            self.dialog.show()