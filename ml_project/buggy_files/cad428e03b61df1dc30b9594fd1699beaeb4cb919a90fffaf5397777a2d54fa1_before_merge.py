    def on_explore_files(self):
        path = os.path.normpath(os.path.join(self.window().tribler_settings['downloadconfig']['saveas'],
		                                     self.selected_item.download_info["destination"]))
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))