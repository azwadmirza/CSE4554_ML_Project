    def on_choose_files_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(self.window(), "Please select the files", "")

        for filename in filenames:
            self.window().create_torrent_files_list.addItem(filename)