    def current_url(self):
        """Get the URL of the current tab.

        Intended to be used from command handlers.

        Return:
            The current URL as QUrl.
        """
        idx = self.currentIndex()
        return super().tab_url(idx)