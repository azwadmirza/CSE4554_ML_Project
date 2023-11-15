    def on_load_finished(self, tab, ok):
        """Adjust tab indicator when loading finished."""
        try:
            idx = self._tab_index(tab)
        except TabDeletedError:
            # We can get signals for tabs we already deleted...
            return
        if ok:
            start = config.val.colors.tabs.indicator.start
            stop = config.val.colors.tabs.indicator.stop
            system = config.val.colors.tabs.indicator.system
            color = utils.interpolate_color(start, stop, 100, system)
        else:
            color = config.val.colors.tabs.indicator.error
        self.widget.set_tab_indicator_color(idx, color)
        self.widget.update_tab_title(idx)
        if idx == self.widget.currentIndex():
            self._update_window_title()
            tab.handle_auto_insert_mode(ok)