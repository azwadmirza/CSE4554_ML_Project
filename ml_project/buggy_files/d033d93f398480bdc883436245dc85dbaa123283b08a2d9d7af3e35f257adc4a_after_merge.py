    def __check_file_status(self, index):
        """Check if file has been changed in any way outside Spyder:
        1. removed, moved or renamed outside Spyder
        2. modified outside Spyder"""
        if self.__file_status_flag:
            # Avoid infinite loop: when the QMessageBox.question pops, it
            # gets focus and then give it back to the CodeEditor instance,
            # triggering a refresh cycle which calls this method
            return
        self.__file_status_flag = True

        if len(self.data) <= index:
            index = self.get_stack_index()

        finfo = self.data[index]
        name = osp.basename(finfo.filename)

        if finfo.newly_created:
            # File was just created (not yet saved): do nothing
            # (do not return because of the clean-up at the end of the method)
            pass

        elif not osp.isfile(finfo.filename):
            # File doesn't exist (removed, moved or offline):
            self.msgbox = QMessageBox(
                    QMessageBox.Warning,
                    self.title,
                    _("<b>%s</b> is unavailable "
                      "(this file may have been removed, moved "
                      "or renamed outside Spyder)."
                      "<br>Do you want to close it?") % name,
                    QMessageBox.Yes | QMessageBox.No,
                    self)
            answer = self.msgbox.exec_()
            if answer == QMessageBox.Yes:
                self.close_file(index)
            else:
                finfo.newly_created = True
                finfo.editor.document().setModified(True)
                self.modification_changed(index=index)

        else:
            # Else, testing if it has been modified elsewhere:
            lastm = QFileInfo(finfo.filename).lastModified()
            if to_text_string(lastm.toString()) \
               != to_text_string(finfo.lastmodified.toString()):
                if finfo.editor.document().isModified():
                    self.msgbox = QMessageBox(
                        QMessageBox.Question,
                        self.title,
                        _("<b>%s</b> has been modified outside Spyder."
                          "<br>Do you want to reload it and lose all "
                          "your changes?") % name,
                        QMessageBox.Yes | QMessageBox.No,
                        self)
                    answer = self.msgbox.exec_()
                    if answer == QMessageBox.Yes:
                        self.reload(index)
                    else:
                        finfo.lastmodified = lastm
                else:
                    self.reload(index)

        # Finally, resetting temporary flag:
        self.__file_status_flag = False