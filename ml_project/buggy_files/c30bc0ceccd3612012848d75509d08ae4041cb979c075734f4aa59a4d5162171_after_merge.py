    def openurl(self, url, *, predict=True):
        """Open the given URL in this tab.

        Arguments:
            url: The QUrl to open.
            predict: If set to False, predicted_navigation is not emitted.
        """
        self._saved_zoom = self.zoom.factor()
        self._openurl_prepare(url, predict=predict)
        self._widget.load(url)