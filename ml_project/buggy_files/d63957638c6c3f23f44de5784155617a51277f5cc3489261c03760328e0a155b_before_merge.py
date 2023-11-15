    def reload(self, *, force=False):
        self.predicted_navigation.emit(self.url())
        if force:
            action = QWebPage.ReloadAndBypassCache
        else:
            action = QWebPage.Reload
        self._widget.triggerPageAction(action)