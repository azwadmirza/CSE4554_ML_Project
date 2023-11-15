    def rename_file(self, fname):
        """Rename file"""
        path, valid = QInputDialog.getText(self, _('Rename'),
                              _('New name:'), QLineEdit.Normal,
                              osp.basename(fname))
        if valid:
            path = osp.join(osp.dirname(fname), to_text_string(path))
            if path == fname:
                return
            if osp.exists(path):
                if QMessageBox.warning(self, _("Rename"),
                         _("Do you really want to rename <b>%s</b> and "
                           "overwrite the existing file <b>%s</b>?"
                           ) % (osp.basename(fname), osp.basename(path)),
                         QMessageBox.Yes|QMessageBox.No) == QMessageBox.No:
                    return
            try:
                misc.rename_file(fname, path)
                if osp.isfile(path):
                    self.sig_renamed.emit(fname, path)
                else:
                    self.sig_renamed_tree.emit(fname, path)
                return path
            except EnvironmentError as error:
                QMessageBox.critical(self, _("Rename"),
                            _("<b>Unable to rename file <i>%s</i></b>"
                              "<br><br>Error message:<br>%s"
                              ) % (osp.basename(fname), to_text_string(error)))