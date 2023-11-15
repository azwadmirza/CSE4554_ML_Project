    def _openurl_prepare(self, url):
        qtutils.ensure_valid(url)
        self.predicted_navigation.emit(url)