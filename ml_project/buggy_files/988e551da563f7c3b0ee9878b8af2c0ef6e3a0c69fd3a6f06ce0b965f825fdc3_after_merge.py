        def on_export_download_request_done(dest_path, data):
            try:
                torrent_file = open(dest_path, "wb")
                torrent_file.write(data)
                torrent_file.close()
            except IOError as exc:
                ConfirmationDialog.show_error(self.window(), "Failure! Exporting channel failed",
                                              "The following occurred when exporting your channel: %s" % str(exc))
            else:
                self.window().tray_show_message("Success! Your channel is exported",
                                                "Your channel metadata file is stored in %s" % dest_path)