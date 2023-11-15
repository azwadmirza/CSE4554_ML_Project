    def buffer(self, index=None, count=None):
        """Select tab by index or url/title best match.

        Focuses window if necessary when index is given. If both index and
        count are given, use count.

        With neither index nor count given, open the qute://tabs page.

        Args:
            index: The [win_id/]index of the tab to focus. Or a substring
                   in which case the closest match will be focused.
            count: The tab index to focus, starting with 1.
        """
        if count is None and index is None:
            self.openurl('qute://tabs/', tab=True)
            return

        if count is not None:
            index = str(count)

        tabbed_browser, tab = self._resolve_buffer_index(index)

        window = tabbed_browser.widget.window()
        window.activateWindow()
        window.raise_()
        tabbed_browser.widget.setCurrentWidget(tab)