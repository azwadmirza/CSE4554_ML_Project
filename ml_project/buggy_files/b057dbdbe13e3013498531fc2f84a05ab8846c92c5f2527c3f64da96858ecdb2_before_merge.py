    def on_torrent_finished(self, torrent_info):
        if self.tray_icon:
            self.window().tray_icon.showMessage("Download finished",
                                                "Download of %s has finished." % torrent_info["name"])