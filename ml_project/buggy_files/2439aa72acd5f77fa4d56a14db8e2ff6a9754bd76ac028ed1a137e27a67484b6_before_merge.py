    def on_icon_changed(self, tab, icon):
        """Set the icon of a tab.

        Slot for the iconChanged signal of any tab.

        Args:
            tab: The WebView where the title was changed.
            icon: The new icon
        """
        if not config.val.tabs.favicons.show:
            return
        try:
            idx = self._tab_index(tab)
        except TabDeletedError:
            # We can get signals for tabs we already deleted...
            return
        self.setTabIcon(idx, icon)
        if config.val.tabs.tabs_are_windows:
            self.window().setWindowIcon(icon)