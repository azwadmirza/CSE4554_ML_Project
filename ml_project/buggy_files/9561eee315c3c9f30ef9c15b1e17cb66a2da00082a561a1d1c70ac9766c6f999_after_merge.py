    def reload(self, *, force=False):
        if self.url().isValid():
            self.predicted_navigation.emit(self.url())

        if force:
            action = QWebEnginePage.ReloadAndBypassCache
        else:
            action = QWebEnginePage.Reload
        self._widget.triggerPageAction(action)