    def closeEvent(self, event):
        if self.confirm_quit:
            reply = QMessageBox.question(self, self.title, localization['global.quitConfirmation'],
                                         QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.No:
                event.ignore()
                return

        event.accept()
        del BrowserView.instances[self.uid]

        try:    # Close inspector if open
            BrowserView.instances[self.uid + '-inspector'].close()
            del BrowserView.instances[self.uid + '-inspector']
        except KeyError:
            pass

        if len(BrowserView.instances) == 0:
            _app.exit()