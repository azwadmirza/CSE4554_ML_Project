    def on_move_files(self):
        if len(self.selected_items) != 1:
            return

        dest_dir = QFileDialog.getExistingDirectory(
            self,
            "Please select the destination directory",
            self.selected_items[0].download_info["destination"],
            QFileDialog.ShowDirsOnly,
        )
        if not dest_dir:
            return

        _infohash = self.selected_items[0].download_info["infohash"]
        _name = self.selected_items[0].download_info["name"]

        data = {"state": "move_storage", "dest_dir": dest_dir}

        TriblerNetworkRequest(
            "downloads/%s" % _infohash,
            lambda res, _, name=_name, target=dest_dir: self.on_files_moved(res, name, target),
            data=data,
            method='PATCH',
        )