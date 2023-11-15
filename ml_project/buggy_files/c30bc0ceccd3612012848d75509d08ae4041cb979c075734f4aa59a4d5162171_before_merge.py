    def openurl(self, url):
        self._saved_zoom = self.zoom.factor()
        self._openurl_prepare(url)
        self._widget.load(url)