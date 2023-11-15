    def on_choose_dir_clicked(self):
        chosen_dir = QFileDialog.getExistingDirectory(self.window(), "Please select the directory containing the files",
                                                      "", QFileDialog.ShowDirsOnly)

        if len(chosen_dir) == 0:
            return

        files = []
        for path, _, dir_files in os.walk(chosen_dir):
            for filename in dir_files:
                files.append(os.path.join(path, filename))

        self.window().create_torrent_files_list.clear()
        for filename in files:
            self.window().create_torrent_files_list.addItem(filename)