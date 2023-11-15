    def openurl(self, url, newtab):
        """Open a URL, used as a slot.

        Args:
            url: The URL to open as QUrl.
            newtab: True to open URL in a new tab, False otherwise.
        """
        qtutils.ensure_valid(url)
        if newtab or self.widget.currentWidget() is None:
            self.tabopen(url, background=False)
        else:
            self.widget.currentWidget().openurl(url)