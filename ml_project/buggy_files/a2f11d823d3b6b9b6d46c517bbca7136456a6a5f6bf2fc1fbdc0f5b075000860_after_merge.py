    def _openurl_prepare(self, url, *, predict=True):
        qtutils.ensure_valid(url)
        if predict:
            self.predicted_navigation.emit(url)