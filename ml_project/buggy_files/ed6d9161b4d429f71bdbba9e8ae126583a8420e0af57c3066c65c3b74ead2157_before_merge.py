    def on_choose_files_clicked(self):
        filenames = QFileDialog.getOpenFileNames(self, "Please select the files", "")

        for filename in filenames[0]:
            self.window().create_torrent_files_list.addItem(filename)