    def reload(self, *, force=False):
        self.predicted_navigation.emit(self.url())
        if force:
            action = QWebEnginePage.ReloadAndBypassCache
        else:
            action = QWebEnginePage.Reload
        self._widget.triggerPageAction(action)