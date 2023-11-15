    def add_path(self):
        self.redirect_stdio.emit(False)
        directory = getexistingdirectory(self, _("Select directory"),
                                         self.last_path)
        self.redirect_stdio.emit(True)
        if directory:
            directory = osp.abspath(directory)
            self.last_path = directory
            if directory in self.pathlist:
                item = self.listwidget.findItems(directory, Qt.MatchExactly)[0]
                item.setCheckState(Qt.Checked)
                answer = QMessageBox.question(self, _("Add path"),
                    _("This directory is already included in Spyder path "
                            "list.<br>Do you want to move it to the top of "
                            "the list?"),
                    QMessageBox.Yes | QMessageBox.No)
                if answer == QMessageBox.Yes:
                    self.pathlist.remove(directory)
                else:
                    return
            self.pathlist.insert(0, directory)
            self.update_list()