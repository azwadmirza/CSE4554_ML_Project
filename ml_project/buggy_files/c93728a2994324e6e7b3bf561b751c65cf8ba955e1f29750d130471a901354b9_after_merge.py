    def on_load_progress(self, tab, perc):
        """Adjust tab indicator on load progress."""
        try:
            idx = self._tab_index(tab)
        except TabDeletedError:
            # We can get signals for tabs we already deleted...
            return
        start = config.val.colors.tabs.indicator.start
        stop = config.val.colors.tabs.indicator.stop
        system = config.val.colors.tabs.indicator.system
        color = utils.interpolate_color(start, stop, perc, system)
        self.widget.set_tab_indicator_color(idx, color)
        self.widget.update_tab_title(idx)
        if idx == self.widget.currentIndex():
            self._update_window_title()