    def on_load_started(self, tab):
        """Clear icon and update title when a tab started loading.

        Args:
            tab: The tab where the signal belongs to.
        """
        try:
            idx = self._tab_index(tab)
        except TabDeletedError:
            # We can get signals for tabs we already deleted...
            return
        self._update_tab_title(idx)
        if tab.data.keep_icon:
            tab.data.keep_icon = False
        else:
            if (config.val.tabs.tabs_are_windows and
                    config.val.tabs.favicons.show):
                self.window().setWindowIcon(self.default_window_icon)
        if idx == self.currentIndex():
            self._update_window_title()