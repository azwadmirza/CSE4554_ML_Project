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
        self.widget.update_tab_title(idx)
        if tab.data.keep_icon:
            tab.data.keep_icon = False
        else:
            if (config.val.tabs.tabs_are_windows and
                    tab.data.should_show_icon()):
                self.widget.window().setWindowIcon(self.default_window_icon)
        if idx == self.widget.currentIndex():
            self._update_window_title()