    def tab_pin(self, count=None):
        """Pin/Unpin the current/[count]th tab.

        Pinning a tab shrinks it to the size of its title text.
        Attempting to close a pinned tab will cause a confirmation,
        unless --force is passed.

        Args:
            count: The tab index to pin or unpin, or None
        """
        tab = self._cntwidget(count)
        if tab is None:
            return

        to_pin = not tab.data.pinned
        self._tabbed_browser.widget.set_tab_pinned(tab, to_pin)