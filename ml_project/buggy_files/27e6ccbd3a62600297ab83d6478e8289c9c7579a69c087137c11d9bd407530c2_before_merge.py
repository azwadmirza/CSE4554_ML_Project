    def close_dialog(self, checked=False):
        if self.rest_request:
            self.rest_request.cancel_request()

        # Loading files label is a clickable label with pyqtsignal which could leak,
        # so delete the widget while closing the dialog.
        if self.dialog_widget and self.dialog_widget.loading_files_label:
            try:
                self.dialog_widget.loading_files_label.deleteLater()
            except RuntimeError:
                logging.debug("Deleting loading files widget in the dialog widget failed.")

        super(StartDownloadDialog, self).close_dialog()