    def on_explore_files(self):
        for selected_item in self.selected_items:
            path = os.path.normpath(selected_item.download_info["destination"])
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))