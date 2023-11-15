    def save_to_file(self, filename, data):
        base_dir = QFileDialog.getExistingDirectory(self, "Select an export directory", "", QFileDialog.ShowDirsOnly)
        if len(base_dir) > 0:
            dest_path = os.path.join(base_dir, filename)
            try:
                with open(dest_path, "wb") as torrent_file:
                    torrent_file.write(json.dumps(data))
            except IOError as exc:
                ConfirmationDialog.show_error(self.window(), "Error exporting file", str(exc))