    def show_in_external_file_explorer(self, fnames=None):
        """Show file in external file explorer"""
        if fnames is None:
            fnames = self.get_current_filename()
        try:
            show_in_external_file_explorer(fnames)
        except FileNotFoundError as error:
            file = str(error).split("'")[1]
            if "xdg-open" in file:
                msg_title = _("Warning")
                msg = _("Spyder can't show this file in the external file "
                        "explorer because the <tt>xdg-utils</tt> package is "
                        "not available on your system.")
                QMessageBox.information(self, msg_title, msg,
                                        QMessageBox.Ok)