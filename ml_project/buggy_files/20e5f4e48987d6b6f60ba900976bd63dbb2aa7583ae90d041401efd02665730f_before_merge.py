    def on_export_download_request_done(self, filename, data):
        dest_path = os.path.join(self.export_dir, filename)
        try:
            torrent_file = open(dest_path, "wb")
            torrent_file.write(data)
            torrent_file.close()
        except IOError as exc:
            ConfirmationDialog.show_error(self.window(),
                                          "Error when exporting file",
                                          "An error occurred when exporting the torrent file: %s" % str(exc))
        else:
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.window().tray_icon.showMessage("Torrent file exported", "Torrent file exported to %s" % dest_path)