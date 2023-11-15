    def openurl(self, url, *, predict=True):
        self._openurl_prepare(url, predict=predict)
        self._widget.openurl(url)